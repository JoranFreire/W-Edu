import 'package:dio/dio.dart';

import '../network/api_error.dart';
import 'cache_local.dart';

/// Cache versionado das telas, no estilo do catálogo do WS-ServicePortal:
///
/// 1. entrega na hora o que está salvo em disco;
/// 2. confere a versão da área (`sync/versions`); igual à salva, termina;
/// 3. senão baixa a tela, salva com a versão e entrega de novo.
///
/// Sem rede e com cache, fica com o cache (funciona offline). A versão é lida
/// antes dos dados: se algo mudar no meio, a próxima conferência baixa de novo.
class Sincronizador {
  Sincronizador(this._cache);

  final CacheLocal _cache;
  final Set<String> _forcadas = {};

  /// Na próxima vez, [chave] ignora o cache e a versão (puxar para atualizar).
  void forcar(String chave) => _forcadas.add(chave);

  /// [dono] separa as contas no mesmo aparelho; [versoes] é a consulta de
  /// versões compartilhada entre as telas (uma requisição por conferência).
  Stream<T> observar<T>({
    required String dono,
    required String chave,
    required String area,
    required Future<Map<String, int>> versoes,
    required Future<Object?> Function() baixar,
    required T Function(Object? json) ler,
  }) async* {
    // A consulta corre enquanto o cache é lido; se falhar antes de ser esperada,
    // o erro não pode escapar como "não tratado" (ele é tratado logo abaixo).
    versoes.ignore();
    final caminho = '$dono/$chave';
    final forcada = _forcadas.remove(chave);
    final salvo = await _cache.ler(caminho);
    if (salvo != null && !forcada) yield ler(salvo.dados);

    try {
      final versao = await _versaoDaArea(versoes, area);
      if (salvo != null && !forcada && versao != null && versao == salvo.versao) return;
      final dados = await baixar();
      final entrega = ler(dados); // valida antes de gravar
      await _cache.salvar(caminho, EntradaCache(versao, dados));
      yield entrega;
    } catch (_) {
      // Com cache já na tela, a falha é silenciosa; sem ele, a tela mostra o erro.
      if (salvo == null || forcada) rethrow;
    }
  }

  /// Regrava a tela depois de uma mudança local (ex.: aviso marcado como lido),
  /// mantendo a versão: a próxima conferência traz a versão nova do servidor.
  Future<void> regravar(String dono, String chave, Object? dados) async {
    final caminho = '$dono/$chave';
    final salvo = await _cache.ler(caminho);
    await _cache.salvar(caminho, EntradaCache(salvo?.versao, dados));
  }

  /// Sem rede, a falha sobe (fica com o cache); servidor sem `sync/versions`
  /// vira versão desconhecida (baixa sempre).
  Future<int?> _versaoDaArea(Future<Map<String, int>> versoes, String area) async {
    try {
      return (await versoes)[area];
    } on DioException catch (erro) {
      if (erroDeRede(erro) || erro.response?.statusCode == 401) rethrow;
      return null;
    }
  }
}
