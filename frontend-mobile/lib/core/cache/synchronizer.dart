import 'package:dio/dio.dart';

import '../network/api_error.dart';
import 'local_cache.dart';

/// Cache versionado das telas, no estilo do catálogo do WS-ServicePortal:
///
/// 1. entrega na hora o que está salvo em disco;
/// 2. confere a versão da área (`sync/versions`); igual à salva, termina;
/// 3. senão baixa a tela, salva com a versão e entrega de novo.
///
/// Sem rede e com cache, fica com o cache (funciona offline). A versão é lida
/// antes dos dados: se algo mudar no meio, a próxima conferência baixa de novo.
class Synchronizer {
  Synchronizer(this._cache);

  final LocalCache _cache;
  final Set<String> _forced = {};

  /// Na próxima vez, [key] ignora o cache e a versão (puxar para atualizar).
  void force(String key) => _forced.add(key);

  /// [owner] separa as contas no mesmo aparelho; [versions] é a consulta de
  /// versões compartilhada entre as telas (uma requisição por conferência).
  Stream<T> watch<T>({
    required String owner,
    required String key,
    required String area,
    required Future<Map<String, int>> versions,
    required Future<Object?> Function() download,
    required T Function(Object? json) parse,
  }) async* {
    // A consulta corre enquanto o cache é lido; se falhar antes de ser esperada,
    // o erro não pode escapar como "não tratado" (ele é tratado logo abaixo).
    versions.ignore();
    final path = '$owner/$key';
    final forced = _forced.remove(key);
    final saved = await _cache.read(path);
    if (saved != null && !forced) yield parse(saved.data);

    try {
      final version = await _areaVersion(versions, area);
      if (saved != null && !forced && version != null && version == saved.version) return;
      final data = await download();
      final parsed = parse(data); // valida antes de gravar
      await _cache.save(path, CacheEntry(version, data));
      yield parsed;
    } catch (_) {
      // Com cache já na tela, a falha é silenciosa; sem ele, a tela mostra o erro.
      if (saved == null || forced) rethrow;
    }
  }

  /// Regrava a tela depois de uma mudança local (ex.: aviso marcado como lido),
  /// mantendo a versão: a próxima conferência traz a versão nova do servidor.
  Future<void> rewrite(String owner, String key, Object? data) async {
    final path = '$owner/$key';
    final saved = await _cache.read(path);
    await _cache.save(path, CacheEntry(saved?.version, data));
  }

  /// Sem rede, a falha sobe (fica com o cache); servidor sem `sync/versions`
  /// vira versão desconhecida (baixa sempre).
  Future<int?> _areaVersion(Future<Map<String, int>> versions, String area) async {
    try {
      return (await versions)[area];
    } on DioException catch (error) {
      if (isNetworkError(error) || error.response?.statusCode == 401) rethrow;
      return null;
    }
  }
}
