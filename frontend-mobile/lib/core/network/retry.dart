import 'api_error.dart';

/// Política de repetição do `ProviderScope`.
///
/// O Riverpod repete sozinho todo provider que falha. Para 401, 403 e 404 a
/// resposta vai ser a mesma — repetir só atrasa a mensagem de erro.
Duration? retryOnlyNetworkErrors(int attempt, Object error) {
  if (attempt >= 2 || !isNetworkError(error)) return null;
  return Duration(seconds: 1 << attempt);
}
