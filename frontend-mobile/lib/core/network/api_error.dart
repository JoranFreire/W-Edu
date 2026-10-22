import 'package:dio/dio.dart';

import '../../l10n/l10n.dart';

/// Primeira mensagem legível de um erro da API.
///
/// Mesma regra do `apiErrorMessage` do web (`frontend/src/lib/api/errors.ts`): o
/// FastAPI devolve o motivo em `detail`, que é texto nas regras de negócio e uma
/// lista de `{msg}` na validação dos campos (422). O `detail` vem no idioma do
/// servidor; o resto (rede, falha genérica) sai do i18n do app.
String apiErrorMessage(Object error, AppLocalizations l10n, {String? fallback}) {
  final generic = fallback ?? l10n.errorGeneric;
  if (error is! DioException) return generic;

  final data = error.response?.data;
  if (data is Map) {
    final detail = data['detail'];
    if (detail is String && detail.isNotEmpty) return detail;
    if (detail is List && detail.isNotEmpty) {
      final first = detail.first;
      if (first is Map && first['msg'] is String) return first['msg'] as String;
    }
  }

  return switch (error.type) {
    DioExceptionType.connectionError || DioExceptionType.connectionTimeout => l10n.errorNoConnection,
    DioExceptionType.receiveTimeout => l10n.errorTimeout,
    _ => generic,
  };
}

/// Código do `detail` (as APIs do Persona respondem com códigos, como `terms_outdated`).
String? apiErrorCode(Object error) {
  if (error is! DioException) return null;
  final data = error.response?.data;
  final detail = data is Map ? data['detail'] : null;
  return detail is String ? detail : null;
}

int? apiStatusCode(Object error) => error is DioException ? error.response?.statusCode : null;

/// Falha de rede, em que tentar de novo pode dar certo — ao contrário de um
/// 403 ou 404, que vão responder a mesma coisa.
bool isNetworkError(Object error) =>
    error is DioException &&
    const {DioExceptionType.connectionError, DioExceptionType.connectionTimeout, DioExceptionType.receiveTimeout}.contains(error.type);
