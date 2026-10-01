import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/cache/cache_local.dart';
import 'package:wedu_mobile/core/cache/sincronizador.dart';

import '../helpers/fakes.dart';

void main() {
  late CacheEmMemoria cache;
  late Sincronizador sincronizador;
  late int downloads;

  setUp(() {
    cache = CacheEmMemoria();
    sincronizador = Sincronizador(cache);
    downloads = 0;
  });

  Future<List<List<String>>> observar({
    Future<Map<String, int>>? versoes,
    String dono = 'i1_u1',
    Object? servidor = const ['novo'],
    bool semRede = false,
  }) {
    return sincronizador
        .observar<List<String>>(
          dono: dono,
          chave: 'agenda',
          area: 'agenda',
          versoes: versoes ?? Future.value({'agenda': 2}),
          baixar: () async {
            downloads++;
            if (semRede) throw DioException.connectionError(requestOptions: RequestOptions(path: 'x'), reason: 'offline');
            return servidor;
          },
          ler: (json) => [for (final item in json as List<dynamic>) item as String],
        )
        .toList();
  }

  Future<void> salvar(int? versao, List<String> dados, {String dono = 'i1_u1'}) =>
      cache.salvar('$dono/agenda', EntradaCache(versao, dados));

  test('sem cache: baixa, entrega e guarda com a versão da área', () async {
    expect(await observar(), [['novo']]);
    expect((await cache.ler('i1_u1/agenda'))!.versao, 2);
  });

  test('versão igual à salva: entrega o cache e não baixa', () async {
    await salvar(2, ['salvo']);
    expect(await observar(), [['salvo']]);
    expect(downloads, 0);
  });

  test('versão mudou: entrega o cache e depois o novo', () async {
    await salvar(1, ['salvo']);
    expect(await observar(), [['salvo'], ['novo']]);
    expect((await cache.ler('i1_u1/agenda'))!.versao, 2);
  });

  test('sem rede com cache: fica com o salvo, sem erro', () async {
    await salvar(1, ['salvo']);
    final semVersoes = Future<Map<String, int>>.delayed(Duration.zero, () => throw semRede(RequestOptions(path: 'sync/versions')));
    expect(await observar(versoes: semVersoes), [['salvo']]);
  });

  test('sem rede e sem cache: a tela recebe o erro', () async {
    await expectLater(observar(semRede: true), throwsA(isA<DioException>()));
  });

  test('forçado (puxar para atualizar): ignora cache e versão', () async {
    await salvar(2, ['salvo']);
    sincronizador.forcar('agenda');
    expect(await observar(), [['novo']]);
    expect(downloads, 1);
  });

  test('forçado sem rede: a falha sobe para a tela avisar', () async {
    await salvar(2, ['salvo']);
    sincronizador.forcar('agenda');
    await expectLater(observar(semRede: true), throwsA(isA<DioException>()));
  });

  test('servidor sem versões: baixa sempre', () async {
    await salvar(null, ['salvo']);
    final req = RequestOptions(path: 'sync/versions');
    final semRota = Future<Map<String, int>>.delayed(
      Duration.zero,
      () => throw DioException.badResponse(statusCode: 404, requestOptions: req, response: Response(requestOptions: req, statusCode: 404)),
    );
    expect(await observar(versoes: semRota), [['salvo'], ['novo']]);
    expect((await cache.ler('i1_u1/agenda'))!.versao, isNull);
  });

  test('cada conta tem o seu cache', () async {
    await salvar(2, ['da ana'], dono: 'i1_ana');
    expect(await observar(dono: 'i1_beto'), [['novo']]);
  });

  test('regravar mantém a versão (a próxima conferência traz a nova)', () async {
    await salvar(2, ['a']);
    await sincronizador.regravar('i1_u1', 'agenda', ['b']);
    final salvo = await cache.ler('i1_u1/agenda');
    expect(salvo!.versao, 2);
    expect(salvo.dados, ['b']);
  });
}
