import 'package:dio/dio.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/network/api_error.dart';
import 'package:wedu_mobile/l10n/l10n.dart';

DioException _response(Object? body, {int status = 400}) {
  final req = RequestOptions(path: 'x');
  return DioException.badResponse(
    statusCode: status,
    requestOptions: req,
    response: Response(requestOptions: req, statusCode: status, data: body),
  );
}

void main() {
  final pt = lookupAppLocalizations(const Locale('pt'));
  final en = lookupAppLocalizations(const Locale('en'));

  test('detail em texto (regra de negócio) vem do servidor como está', () {
    expect(apiErrorMessage(_response({'detail': 'Credenciais inválidas'}), pt), 'Credenciais inválidas');
  });

  test('detail em lista (validação 422) usa a primeira mensagem', () {
    final error = _response({
      'detail': [
        {
          'msg': 'value is not a valid email address',
          'loc': ['body', 'email'],
        },
      ],
    }, status: 422);
    expect(apiErrorMessage(error, pt), 'value is not a valid email address');
  });

  test('sem conexão tem mensagem própria, no idioma da tela, e é erro de rede', () {
    final error = DioException.connectionError(
      requestOptions: RequestOptions(path: 'x'),
      reason: 'offline',
    );
    expect(apiErrorMessage(error, pt), pt.errorNoConnection);
    expect(apiErrorMessage(error, en), en.errorNoConnection);
    expect(isNetworkError(error), isTrue);
    expect(isNetworkError(_response({'detail': 'x'}, status: 403)), isFalse);
  });

  test('erro desconhecido usa o texto padrão', () {
    expect(apiErrorMessage(StateError('x'), pt, fallback: 'Padrão'), 'Padrão');
    expect(apiErrorMessage(StateError('x'), pt), pt.errorGeneric);
  });
}
