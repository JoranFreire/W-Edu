import 'package:dio/dio.dart';

/// Primeira mensagem legível de um erro da API.
///
/// Mesma regra do `apiErrorMessage` do web (`frontend/src/lib/api/errors.ts`): o
/// FastAPI devolve o motivo em `detail`, que é texto nas regras de negócio e uma
/// lista de `{msg}` na validação dos campos (422).
String mensagemDeErro(Object erro, [String padrao = 'Não foi possível concluir.']) {
  if (erro is! DioException) return padrao;

  final dados = erro.response?.data;
  if (dados is Map) {
    final detalhe = dados['detail'];
    if (detalhe is String && detalhe.isNotEmpty) return detalhe;
    if (detalhe is List && detalhe.isNotEmpty) {
      final primeiro = detalhe.first;
      if (primeiro is Map && primeiro['msg'] is String) return primeiro['msg'] as String;
    }
  }

  return switch (erro.type) {
    DioExceptionType.connectionError ||
    DioExceptionType.connectionTimeout =>
      'Sem conexão com o servidor. Verifique a internet.',
    DioExceptionType.receiveTimeout => 'O servidor demorou a responder.',
    _ => padrao,
  };
}

/// Falha de rede, em que tentar de novo pode dar certo — ao contrário de um
/// 403 ou 404, que vão responder a mesma coisa.
bool erroDeRede(Object erro) =>
    erro is DioException &&
    const {
      DioExceptionType.connectionError,
      DioExceptionType.connectionTimeout,
      DioExceptionType.receiveTimeout,
    }.contains(erro.type);
