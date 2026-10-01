import 'package:dio/dio.dart';

import '../../../core/network/token_store.dart';
import 'instituicao.dart';
import 'usuario.dart';

class AuthRepository {
  AuthRepository(this._dio, this._tokens);

  final Dio _dio;
  final TokenStore _tokens;

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
    return Usuario.fromJson(pessoa.data!, Instituicao.fromJson(instituicao.data!));
  }

  /// A API não guarda sessão no servidor: sair é esquecer o token no aparelho.
  Future<void> sair() => _tokens.limpar();
}
