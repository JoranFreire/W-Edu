import 'package:dio/dio.dart';

import '../../../core/cache/cache_local.dart';
import '../../../core/network/token_store.dart';
import 'instituicao.dart';
import 'usuario.dart';

class AuthRepository {
  AuthRepository(this._dio, this._tokens, this._cache);

  final Dio _dio;
  final TokenStore _tokens;
  final CacheLocal _cache;

  /// Pessoa e instituição da última conferência: o app abre com elas sem esperar a rede.
  static const _chaveSessao = 'sessao';

  Future<bool> temSessao() async => await _tokens.ler() != null;

  Future<Usuario> entrar(String email, String senha) async {
    final resposta = await _dio.post<Map<String, dynamic>>(
      'auth/login',
      data: {'email': email.trim(), 'password': senha},
    );
    await _tokens.salvar(resposta.data!['access_token'] as String);
    return eu();
  }

  /// A pessoa e a instituição ativa (a do token), juntas. `Future.wait` repassa
  /// o próprio erro da API (o `.wait` de record o embrulharia e o 401 se perderia).
  Future<Usuario> eu() async {
    final [pessoa, instituicao] = await Future.wait([
      _dio.get<Map<String, dynamic>>('users/me'),
      _dio.get<Map<String, dynamic>>('institutions/current'),
    ]);
    final dados = {'usuario': pessoa.data!, 'instituicao': instituicao.data!};
    final usuario = _ler(dados);
    await _cache.salvar(_chaveSessao, EntradaCache(null, dados));
    return usuario;
  }

  Future<Usuario?> sessaoSalva() async {
    final salva = await _cache.ler(_chaveSessao);
    if (salva == null) return null;
    try {
      return _ler(salva.dados);
    } on Object {
      return null;
    }
  }

  /// A API não guarda sessão no servidor: sair é esquecer o token e os dados
  /// pessoais guardados no aparelho.
  Future<void> sair() async {
    await _tokens.limpar();
    await _cache.limpar();
  }

  Usuario _ler(Object? dados) {
    final json = dados as Map<String, dynamic>;
    return Usuario.fromJson(json['usuario'] as Map<String, dynamic>, Instituicao.fromJson(json['instituicao'] as Map<String, dynamic>));
  }
}
