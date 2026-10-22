import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:wedu_mobile/core/cache/local_cache.dart';

import 'helpers/fakes.dart';
import 'helpers/session_harness.dart';

void main() {
  late SessionHarness h;

  setUpAll(initializeDateFormatting);
  setUp(() => h = SessionHarness());

  testWidgets('login recusado mostra a mensagem da API', (tester) => _rejectedLoginShowsApiMessage(tester, h));
  testWidgets('aluno entra e vê as abas de aluno', (tester) => _studentSeesStudentTabs(tester, h));
  testWidgets('responsável com sessão salva vê os dependentes', (tester) => _guardianWithSavedSessionSeesDependents(tester, h));
  testWidgets('token expirado volta para o login', (tester) => _expiredTokenBackToLogin(tester, h));
  testWidgets('sem rede, abre com a sessão e as telas salvas', (tester) => _offlineOpensSavedSessionAndScreens(tester, h));
  testWidgets('versão igual à salva não baixa a tela de novo', (tester) => _sameVersionDoesNotRefetch(tester, h));
  testWidgets('sair apaga o cache da conta', (tester) => _signOutClearsAccountCache(tester, h));
  testWidgets('sessão salva com token recusado volta ao login e apaga o cache', (tester) => _rejectedSavedTokenClearsCache(tester, h));
  testWidgets('aluno abre o QR do benefício liberado, mesmo sem rede', (tester) => _studentOpensBenefitQrOffline(tester, h));
  testWidgets('sem benefício liberado, o início não mostra o cartão', (tester) => _noBenefitNoHomeCard(tester, h));
  testWidgets(
    'professor abre o QR de retirada da requisição aprovada, mesmo sem rede',
    (tester) => _teacherOpensPickupQrOffline(tester, h),
  );
  testWidgets('sem permissão de requisitar, o início não mostra materiais', (tester) => _noRequestPermissionNoMaterials(tester, h));
  testWidgets('em inglês, a tela segue o idioma', (tester) => _englishFollowsLocale(tester, h));
}

Future<void> _rejectedLoginShowsApiMessage(WidgetTester tester, SessionHarness h) async {
  h.server.on('POST auth/login', (_) => (401, {'detail': 'E-mail ou senha incorretos'}));
  await h.openApp(tester);

  await h.signIn(tester);

  expect(find.text('E-mail ou senha incorretos'), findsOneWidget);
  expect(h.tokens.current, isNull);
}

Future<void> _studentSeesStudentTabs(WidgetTester tester, SessionHarness h) async {
  h.server
    ..on('POST auth/login', (_) => (200, {'access_token': 't-1', 'token_type': 'bearer'}))
    ..on('GET users/me', (_) => (200, userJson()));
  await h.openApp(tester);

  await h.signIn(tester);

  expect(h.tokens.current, 't-1');
  expect(find.text('Olá, Ana!'), findsOneWidget);
  expect(find.text('Boletim'), findsOneWidget);
  expect(find.text('Dependentes'), findsNothing);
}

Future<void> _guardianWithSavedSessionSeesDependents(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  h.server.on('GET users/me', (_) => (200, userJson(role: 'guardian')));
  await h.openApp(tester);

  expect(find.text('Olá, Ana!'), findsOneWidget);
  expect(find.text('Boletim'), findsNothing);
  await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Dependentes')));
  await tester.pumpAndSettle();
  expect(find.text('Bruno Souza'), findsWidgets);
}

Future<void> _expiredTokenBackToLogin(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 'vencido';
  h.server.on('GET users/me', (_) => (401, {'detail': 'Token inválido'}));
  await h.openApp(tester);

  expect(find.text('Entrar'), findsOneWidget);
  expect(h.tokens.current, isNull);
}

Future<void> _offlineOpensSavedSessionAndScreens(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  const owner = 'i-1_u-1';
  await h.cache.save('session', CacheEntry(null, {'user': userJson(), 'institution': institutionJson()}));
  await h.cache.save('$owner/notices_summary', const CacheEntry(1, {'unread': 2, 'total': 2}));
  await h.cache.save('$owner/agenda', CacheEntry(1, [agendaJson('ag1')]));
  for (final route in [
    'GET users/me',
    'GET institutions/current',
    'GET sync/versions',
    'GET notifications/me/summary',
    'GET school/my/agenda',
  ]) {
    h.server.on(route, (req) => throw offline(req));
  }
  await h.openApp(tester);

  expect(find.text('Olá, Ana!'), findsOneWidget);
  expect(find.text('2 sem ler'), findsOneWidget);
  expect(find.textContaining('Prova bimestral'), findsOneWidget);
}

Future<void> _sameVersionDoesNotRefetch(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  h.server.on('GET users/me', (_) => (200, userJson()));
  await h.cache.save('i-1_u-1/agenda', CacheEntry(1, [agendaJson('ag1')]));
  await h.openApp(tester);

  expect(find.textContaining('Prova bimestral'), findsOneWidget);
  expect(h.server.count('GET school/my/agenda'), 0);
  expect(h.server.count('GET notifications/me/summary'), 1);
}

Future<void> _signOutClearsAccountCache(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  h.server.on('GET users/me', (_) => (200, userJson()));
  await h.openApp(tester);
  expect(h.cache.entries, isNotEmpty);

  await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Sair'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Sair').last);
  await tester.pumpAndSettle();

  expect(find.text('Entrar'), findsOneWidget);
  expect(h.cache.entries, isEmpty);
  expect(h.tokens.current, isNull);
}

Future<void> _rejectedSavedTokenClearsCache(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 'vencido';
  await h.cache.save('session', CacheEntry(null, {'user': userJson(), 'institution': institutionJson()}));
  for (final route in ['GET users/me', 'GET sync/versions', 'GET notifications/me/summary', 'GET school/my/agenda']) {
    h.server.on(route, (_) => (401, {'detail': 'Token inválido'}));
  }
  await h.openApp(tester);

  expect(find.text('Entrar'), findsOneWidget);
  expect(h.tokens.current, isNull);
  expect(h.cache.entries, isEmpty);
}

Future<void> _studentOpensBenefitQrOffline(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  await h.cache.save('session', CacheEntry(null, {'user': userJson(), 'institution': institutionJson()}));
  await h.cache.save(
    'i-1_u-1/benefits',
    CacheEntry(1, [benefitJson('1', validUntil: '2099-12-31'), benefitJson('2', status: 'redeemed', item: 'Kit', kind: 'material')]),
  );
  for (final route in [
    'GET users/me',
    'GET institutions/current',
    'GET sync/versions',
    'GET notifications/me/summary',
    'GET school/my/agenda',
    'GET social/my/vouchers',
  ]) {
    h.server.on(route, (req) => throw offline(req));
  }
  await h.openApp(tester);

  expect(find.text('1 para retirar'), findsOneWidget);
  await tester.tap(find.text('Benefícios'));
  await tester.pumpAndSettle();
  expect(find.text('Retirado'), findsOneWidget);
  expect(find.text('Material'), findsOneWidget);
  await tester.tap(find.text('Mostrar QR'));
  await tester.pumpAndSettle();
  expect(find.byType(QrImageView), findsOneWidget);
  expect(find.text('COD1'), findsOneWidget);
}

Future<void> _noBenefitNoHomeCard(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  h.server.on('GET users/me', (_) => (200, userJson()));
  await h.openApp(tester);
  expect(find.text('Olá, Ana!'), findsOneWidget);
  expect(find.text('Benefícios'), findsNothing);
}

Future<void> _teacherOpensPickupQrOffline(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  await h.cache.save(
    'session',
    CacheEntry(null, {
      'user': userJson(role: 'instructor'),
      'institution': institutionJson(),
      'access': accessJson(permissions: ['warehouse.request']),
    }),
  );
  await h.cache.save(
    'i-1_u-1/material_requests',
    CacheEntry(1, [materialRequestJson('r1', code: 'RET123'), materialRequestJson('r2', status: 'pending')]),
  );
  for (final route in [
    'GET users/me',
    'GET institutions/current',
    'GET access/me',
    'GET sync/versions',
    'GET notifications/me/summary',
    'GET warehouse/my/requests',
  ]) {
    h.server.on(route, (req) => throw offline(req));
  }
  await h.openApp(tester);

  expect(find.text('1 para retirar'), findsOneWidget);
  await tester.tap(find.text('Requisições de material'));
  await tester.pumpAndSettle();
  expect(find.text('Aguardando aprovação'), findsOneWidget);
  await tester.tap(find.text('QR de retirada'));
  await tester.pumpAndSettle();
  expect(find.byType(QrImageView), findsOneWidget);
  expect(find.text('RET123'), findsOneWidget);
}

Future<void> _noRequestPermissionNoMaterials(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  h.server.on('GET users/me', (_) => (200, userJson()));
  await h.openApp(tester);
  expect(find.text('Olá, Ana!'), findsOneWidget);
  expect(find.text('Requisições de material'), findsNothing);
}

Future<void> _englishFollowsLocale(WidgetTester tester, SessionHarness h) async {
  h.tokens.current = 't-1';
  h.server.on('GET users/me', (_) => (200, userJson()));
  await h.openApp(tester, locale: const Locale('en'));

  expect(find.text('Hi, Ana!'), findsOneWidget);
  expect(find.text('Report card'), findsOneWidget);
  expect(find.text('Boletim'), findsNothing);
}
