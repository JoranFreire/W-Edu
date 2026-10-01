import 'package:dio/dio.dart';

import 'token_store.dart';

/// Põe o token em cada requisição e, se a API responder 401 (token vencido ou
/// conta desativada), esquece a sessão e avisa — não há refresh para tentar.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this._tokens, required this._onSessaoExpirada});

  final TokenStore _tokens;
  final void Function() _onSessaoExpirada;

  static const _rotasPublicas = ['auth/login', 'public/'];

  bool _publica(RequestOptions opcoes) => _rotasPublicas.any((rota) => opcoes.path.contains(rota));

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (!_publica(options)) {
      final token = await _tokens.ler();
      if (token != null) options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final opcoes = err.requestOptions;
    if (err.response?.statusCode == 401 && !_publica(opcoes) && await _tokens.ler() != null) {
      await _tokens.limpar();
      _onSessaoExpirada();
    }
    handler.next(err);
  }
}
