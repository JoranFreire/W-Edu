import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/api_config.dart';
import '../config/persona_config.dart';
import 'auth_interceptor.dart';
import 'token_store.dart';

/// O cliente HTTP que todas as features usam. Nos testes, basta sobrescrever
/// `tokenStoreProvider` ou `httpAdapterProvider` para trocar o que está por baixo.

final tokenStoreProvider = Provider<TokenStore>((ref) => SecureTokenStore());

/// Nulo = o adapter padrão do dio. Os testes põem aqui um servidor falso e
/// exercitam o resto da ligação (interceptor, repositórios) de verdade.
final httpAdapterProvider = Provider<HttpClientAdapter?>((ref) => null);

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: {'Accept': 'application/json'},
    ),
  );
  final adapter = ref.watch(httpAdapterProvider);
  if (adapter != null) dio.httpClientAdapter = adapter;
  dio.interceptors.add(
    AuthInterceptor(tokens: ref.watch(tokenStoreProvider), onSessionExpired: () => ref.read(sessionExpiredProvider.notifier).notify()),
  );
  return dio;
});

/// Endereço do Persona; nulo desliga o reconhecimento facial. Os testes o sobrescrevem.
final personaBaseUrlProvider = Provider<String?>((ref) => PersonaConfig.baseUrl);

/// Cliente do Persona (segundo dio, como na ADR 0012). Nulo quando desligado.
/// Usa o mesmo token do W-Edu (o Persona o confere); o login facial vai sem token.
final personaDioProvider = Provider<Dio?>((ref) {
  final baseUrl = ref.watch(personaBaseUrlProvider);
  if (baseUrl == null) return null;
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      // Envio das fotos e conferência do rosto levam mais que uma requisição comum.
      receiveTimeout: const Duration(seconds: 60),
      headers: {'Accept': 'application/json'},
    ),
  );
  final adapter = ref.watch(httpAdapterProvider);
  if (adapter != null) dio.httpClientAdapter = adapter;
  dio.interceptors.add(
    AuthInterceptor(
      tokens: ref.watch(tokenStoreProvider),
      onSessionExpired: () => ref.read(sessionExpiredProvider.notifier).notify(),
      publicRoutes: AuthInterceptor.personaPublicRoutes,
    ),
  );
  return dio;
});

/// Muda a cada vez que a API recusa o token. O core só avisa; quem decide o
/// que fazer (voltar ao login) é a feature de auth, que escuta isto. Assim a
/// rede não precisa conhecer nenhuma feature.
final sessionExpiredProvider = NotifierProvider<SessionExpired, int>(SessionExpired.new);

class SessionExpired extends Notifier<int> {
  @override
  int build() => 0;

  void notify() => state++;
}
