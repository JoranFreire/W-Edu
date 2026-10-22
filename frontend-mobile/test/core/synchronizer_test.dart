import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/fakes.dart';
import '../helpers/sync_harness.dart';

void main() {
  late SyncHarness h;

  setUp(() => h = SyncHarness());
  group('cache e versão da área', () => _cacheAndVersions(() => h));
  group('forçado e servidor sem versões', () => _forcedAndUnversioned(() => h));
  group('contas', () => _accounts(() => h));
}

void _cacheAndVersions(SyncHarness Function() h) {
  test('sem h().cache: baixa, entrega e guarda com a versão da área', () async {
    expect(await h().watch(), [
      ['new'],
    ]);
    expect((await h().cache.read('i1_u1/agenda'))!.version, 2);
  });

  test('versão igual à salva: entrega o h().cache e não baixa', () async {
    await h().store(2, ['saved']);
    expect(await h().watch(), [
      ['saved'],
    ]);
    expect(h().downloads, 0);
  });

  test('versão mudou: entrega o h().cache e depois o novo', () async {
    await h().store(1, ['saved']);
    expect(await h().watch(), [
      ['saved'],
      ['new'],
    ]);
    expect((await h().cache.read('i1_u1/agenda'))!.version, 2);
  });

  test('sem rede com h().cache: fica com o salvo, sem erro', () async {
    await h().store(1, ['saved']);
    final noVersions = Future<Map<String, int>>.delayed(Duration.zero, () => throw offline(RequestOptions(path: 'sync/versions')));
    expect(await h().watch(versions: noVersions), [
      ['saved'],
    ]);
  });

  test('sem rede e sem h().cache: a tela recebe o erro', () async {
    await expectLater(h().watch(isOffline: true), throwsA(isA<DioException>()));
  });
}

void _forcedAndUnversioned(SyncHarness Function() h) {
  test('forçado (puxar para atualizar): ignora h().cache e versão', () async {
    await h().store(2, ['saved']);
    h().synchronizer.force('agenda');
    expect(await h().watch(), [
      ['new'],
    ]);
    expect(h().downloads, 1);
  });

  test('forçado sem rede: a falha sobe para a tela avisar', () async {
    await h().store(2, ['saved']);
    h().synchronizer.force('agenda');
    await expectLater(h().watch(isOffline: true), throwsA(isA<DioException>()));
  });

  test('servidor sem versões: baixa sempre', () async {
    await h().store(null, ['saved']);
    final req = RequestOptions(path: 'sync/versions');
    final noRoute = Future<Map<String, int>>.delayed(
      Duration.zero,
      () => throw DioException.badResponse(
        statusCode: 404,
        requestOptions: req,
        response: Response(requestOptions: req, statusCode: 404),
      ),
    );
    expect(await h().watch(versions: noRoute), [
      ['saved'],
      ['new'],
    ]);
    expect((await h().cache.read('i1_u1/agenda'))!.version, isNull);
  });
}

void _accounts(SyncHarness Function() h) {
  test('cada conta tem o seu h().cache', () async {
    await h().store(2, ['anas'], owner: 'i1_ana');
    expect(await h().watch(owner: 'i1_beto'), [
      ['new'],
    ]);
  });

  test('regravar mantém a versão (a próxima conferência traz a nova)', () async {
    await h().store(2, ['a']);
    await h().synchronizer.rewrite('i1_u1', 'agenda', ['b']);
    final saved = await h().cache.read('i1_u1/agenda');
    expect(saved!.version, 2);
    expect(saved.data, ['b']);
  });
}
