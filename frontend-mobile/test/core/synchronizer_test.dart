import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/cache/local_cache.dart';
import 'package:wedu_mobile/core/cache/synchronizer.dart';

import '../helpers/fakes.dart';

void main() {
  late InMemoryCache cache;
  late Synchronizer synchronizer;
  late int downloads;

  setUp(() {
    cache = InMemoryCache();
    synchronizer = Synchronizer(cache);
    downloads = 0;
  });

  Future<List<List<String>>> watch({
    Future<Map<String, int>>? versions,
    String owner = 'i1_u1',
    Object? serverData = const ['new'],
    bool isOffline = false,
  }) {
    return synchronizer
        .watch<List<String>>(
          owner: owner,
          key: 'agenda',
          area: 'agenda',
          versions: versions ?? Future.value({'agenda': 2}),
          download: () async {
            downloads++;
            if (isOffline) throw offline(RequestOptions(path: 'x'));
            return serverData;
          },
          parse: (json) => [for (final item in json as List<dynamic>) item as String],
        )
        .toList();
  }

  Future<void> store(int? version, List<String> data, {String owner = 'i1_u1'}) => cache.save('$owner/agenda', CacheEntry(version, data));

  test('sem cache: baixa, entrega e guarda com a versão da área', () async {
    expect(await watch(), [
      ['new'],
    ]);
    expect((await cache.read('i1_u1/agenda'))!.version, 2);
  });

  test('versão igual à salva: entrega o cache e não baixa', () async {
    await store(2, ['saved']);
    expect(await watch(), [
      ['saved'],
    ]);
    expect(downloads, 0);
  });

  test('versão mudou: entrega o cache e depois o novo', () async {
    await store(1, ['saved']);
    expect(await watch(), [
      ['saved'],
      ['new'],
    ]);
    expect((await cache.read('i1_u1/agenda'))!.version, 2);
  });

  test('sem rede com cache: fica com o salvo, sem erro', () async {
    await store(1, ['saved']);
    final noVersions = Future<Map<String, int>>.delayed(Duration.zero, () => throw offline(RequestOptions(path: 'sync/versions')));
    expect(await watch(versions: noVersions), [
      ['saved'],
    ]);
  });

  test('sem rede e sem cache: a tela recebe o erro', () async {
    await expectLater(watch(isOffline: true), throwsA(isA<DioException>()));
  });

  test('forçado (puxar para atualizar): ignora cache e versão', () async {
    await store(2, ['saved']);
    synchronizer.force('agenda');
    expect(await watch(), [
      ['new'],
    ]);
    expect(downloads, 1);
  });

  test('forçado sem rede: a falha sobe para a tela avisar', () async {
    await store(2, ['saved']);
    synchronizer.force('agenda');
    await expectLater(watch(isOffline: true), throwsA(isA<DioException>()));
  });

  test('servidor sem versões: baixa sempre', () async {
    await store(null, ['saved']);
    final req = RequestOptions(path: 'sync/versions');
    final noRoute = Future<Map<String, int>>.delayed(
      Duration.zero,
      () => throw DioException.badResponse(
        statusCode: 404,
        requestOptions: req,
        response: Response(requestOptions: req, statusCode: 404),
      ),
    );
    expect(await watch(versions: noRoute), [
      ['saved'],
      ['new'],
    ]);
    expect((await cache.read('i1_u1/agenda'))!.version, isNull);
  });

  test('cada conta tem o seu cache', () async {
    await store(2, ['anas'], owner: 'i1_ana');
    expect(await watch(owner: 'i1_beto'), [
      ['new'],
    ]);
  });

  test('regravar mantém a versão (a próxima conferência traz a nova)', () async {
    await store(2, ['a']);
    await synchronizer.rewrite('i1_u1', 'agenda', ['b']);
    final saved = await cache.read('i1_u1/agenda');
    expect(saved!.version, 2);
    expect(saved.data, ['b']);
  });
}
