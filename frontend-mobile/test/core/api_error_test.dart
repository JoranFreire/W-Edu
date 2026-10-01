import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/network/api_error.dart';

DioException _resposta(Object? corpo, {int status = 400}) {
  final req = RequestOptions(path: 'x');
  return DioException.badResponse(statusCode: status, requestOptions: req, response: Response(requestOptions: req, statusCode: status, data: corpo));
}

void main() {
  test('detail em texto (regra de negócio)', () {
    expect(mensagemDeErro(_resposta({'detail': 'Credenciais inválidas'})), 'Credenciais inválidas');
  });

  test('detail em lista (validação 422) usa a primeira mensagem', () {
    final erro = _resposta({'detail': [{'msg': 'value is not a valid email address', 'loc': ['body', 'email']}]}, status: 422);
    expect(mensagemDeErro(erro), 'value is not a valid email address');
  });

  test('sem conexão tem mensagem própria e é erro de rede', () {
    final erro = DioException.connectionError(requestOptions: RequestOptions(path: 'x'), reason: 'offline');
    expect(mensagemDeErro(erro), contains('Sem conexão'));
    expect(erroDeRede(erro), isTrue);
    expect(erroDeRede(_resposta({'detail': 'x'}, status: 403)), isFalse);
  });

  test('erro desconhecido usa o texto padrão', () {
    expect(mensagemDeErro(StateError('x'), 'Padrão'), 'Padrão');
  });
}
