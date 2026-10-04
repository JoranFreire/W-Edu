import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/network/auth_interceptor.dart';

import '../helpers/fakes.dart';

void main() {
  late FakeServer server;
  late InMemoryTokenStore tokens;
  late int expired;
  late Dio dio;

  setUp(() {
    server = FakeServer();
    tokens = InMemoryTokenStore('t-1');
    expired = 0;
    dio = Dio(BaseOptions(baseUrl: 'http://api/'))
      ..httpClientAdapter = server
      ..interceptors.add(AuthInterceptor(tokens: tokens, onSessionExpired: () => expired++));
  });

  test('envia o token nas rotas autenticadas', () async {
    server.on('GET users/me', (req) => (200, {'auth': req.headers['Authorization']}));
    final response = await dio.get<Map<String, dynamic>>('users/me');
    expect(response.data!['auth'], 'Bearer t-1');
  });

  test('não envia token no login nem nas rotas públicas', () async {
    server
      ..on('POST auth/login', (req) => (200, {'auth': req.headers['Authorization']}))
      ..on('GET public/plans', (req) => (200, {'auth': req.headers['Authorization']}));
    expect((await dio.post<Map<String, dynamic>>('auth/login')).data!['auth'], isNull);
    expect((await dio.get<Map<String, dynamic>>('public/plans')).data!['auth'], isNull);
  });

  test('401 esquece o token e avisa que a sessão acabou', () async {
    server.on('GET users/me', (_) => (401, {'detail': 'Token inválido'}));
    await expectLater(dio.get<void>('users/me'), throwsA(isA<DioException>()));
    expect(tokens.current, isNull);
    expect(expired, 1);
  });

  test('403 não derruba a sessão', () async {
    server.on('GET assessment/my/report-card', (_) => (403, {'detail': 'Acesso restrito'}));
    await expectLater(dio.get<void>('assessment/my/report-card'), throwsA(isA<DioException>()));
    expect(tokens.current, 't-1');
    expect(expired, 0);
  });

  test('falha de rede não derruba a sessão', () async {
    server.on('GET users/me', (req) => throw offline(req));
    await expectLater(dio.get<void>('users/me'), throwsA(isA<DioException>()));
    expect(tokens.current, 't-1');
    expect(expired, 0);
  });
}
