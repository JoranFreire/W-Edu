import 'package:dio/dio.dart';

import 'token_store.dart';

/// Põe o token em cada requisição e, se a API responder 401 (token vencido ou
/// conta desativada), esquece a sessão e avisa — não há refresh para tentar.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this._tokens, required this._onSessaoExpirada, this._rotasPublicas = rotasPublicasDoWEdu});

  final TokenStore _tokens;
  final void Function() _onSessaoExpirada;

  /// Rotas sem token: quem chama ainda não entrou (e um 401 nelas é recusa, não sessão vencida).
  final List<String> _rotasPublicas;

  static const rotasPublicasDoWEdu = ['auth/login', 'auth/facial-login', 'public/'];

  /// No Persona, o login facial (desafio e conferência) é sem token; o resto usa o token do W-Edu.
  static const rotasPublicasDoPersona = ['liveness/login-challenge', 'auth/face/', 'consent/terms/'];

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
