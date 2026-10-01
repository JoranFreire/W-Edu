import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/api_config.dart';
import 'auth_interceptor.dart';
import 'token_store.dart';

/// O cliente HTTP que todas as features usam. Nos testes, basta sobrescrever
/// `tokenStoreProvider` ou `httpAdapterProvider` para trocar o que está por baixo.

final tokenStoreProvider = Provider<TokenStore>((ref) => SecureTokenStore());

/// Nulo = o adapter padrão do dio. Os testes põem aqui um servidor falso e
/// exercitam o resto da ligação (interceptor, repositórios) de verdade.
final httpAdapterProvider = Provider<HttpClientAdapter?>((ref) => null);

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: ApiConfig.baseUrl,
    connectTimeout: ApiConfig.connectTimeout,
    receiveTimeout: ApiConfig.receiveTimeout,
    headers: {'Accept': 'application/json'},
  ));
  final adapter = ref.watch(httpAdapterProvider);
  if (adapter != null) dio.httpClientAdapter = adapter;
  dio.interceptors.add(AuthInterceptor(
    tokens: ref.watch(tokenStoreProvider),
    onSessaoExpirada: () => ref.read(sessaoExpiradaProvider.notifier).avisar(),
  ));
  return dio;
});

/// Muda a cada vez que a API recusa o token. O core só avisa; quem decide o
/// que fazer (voltar ao login) é a feature de auth, que escuta isto. Assim a
/// rede não precisa conhecer nenhuma feature.
final sessaoExpiradaProvider = NotifierProvider<SessaoExpirada, int>(SessaoExpirada.new);

class SessaoExpirada extends Notifier<int> {
  @override
  int build() => 0;

  void avisar() => state++;
}
