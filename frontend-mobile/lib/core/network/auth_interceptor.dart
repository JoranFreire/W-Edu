import 'package:dio/dio.dart';

import 'token_store.dart';

/// Põe o token em cada requisição e, se a API responder 401 (token vencido ou
/// conta desativada), esquece a sessão e avisa — não há refresh para tentar.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this._tokens, required this._onSessionExpired, this._publicRoutes = wEduPublicRoutes});

  final TokenStore _tokens;
  final void Function() _onSessionExpired;

  /// Rotas sem token: quem chama ainda não entrou (e um 401 nelas é recusa, não sessão vencida).
  final List<String> _publicRoutes;

  static const wEduPublicRoutes = ['auth/login', 'auth/facial-login', 'public/'];

  /// No Persona, o login facial (desafio e conferência) é sem token; o resto usa o token do W-Edu.
  static const personaPublicRoutes = ['liveness/login-challenge', 'auth/face/', 'consent/terms/'];

  bool _isPublic(RequestOptions options) => _publicRoutes.any((route) => options.path.contains(route));

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (!_isPublic(options)) {
      final token = await _tokens.read();
      if (token != null) options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401 && !_isPublic(err.requestOptions) && await _tokens.read() != null) {
      await _tokens.clear();
      _onSessionExpired();
    }
    handler.next(err);
  }
}
