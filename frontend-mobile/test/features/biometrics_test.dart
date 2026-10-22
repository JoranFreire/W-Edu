import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

import '../helpers/biometrics_harness.dart';

void main() {
  late BiometricsHarness h;

  setUpAll(initializeDateFormatting);
  setUp(() => h = BiometricsHarness());

  testWidgets('adulto autoriza o login depois de ler o termo', (tester) => _adultGrantsLoginAfterTerms(tester, h));
  testWidgets('fechar o termo sem concordar não autoriza', (tester) => _closingTermsDoesNotGrant(tester, h));
  testWidgets('termo desatualizado pede para ler de novo', (tester) => _outdatedTermsAskToReread(tester, h));
  testWidgets('revogar pede confirmação', (tester) => _revokeAsksConfirmation(tester, h));
  testWidgets('cadastra o rosto com o token do W-Edu e uma foto por passo', (tester) => _enrollsWithTokenAndPhotoPerStep(tester, h));
  testWidgets('foto ruim: explica e deixa tentar de novo', (tester) => _badPhotoExplainsAndRetries(tester, h));
  testWidgets('menor de 16 não autoriza sozinho', (tester) => _under16CannotGrantAlone(tester, h));
  testWidgets(
    'com 16 ou 17 anos autoriza login e catraca, mas não a presença',
    (tester) => _teenGrantsLoginAndAccessNotAttendance(tester, h),
  );
  testWidgets('dependente com 16 anos ou mais decide sozinho', (tester) => _dependent16DecidesAlone(tester, h));
  testWidgets('responsável autoriza a catraca do dependente menor de 16', (tester) => _guardianGrantsAccessForUnder16(tester, h));
  testWidgets('sem o Persona, nada de rosto no perfil nem no dependente', (tester) => _noPersonaNoFaceAnywhere(tester, h));
}

Future<void> _adultGrantsLoginAfterTerms(WidgetTester tester, BiometricsHarness h) async {
  Object? sent;
  h.server.on('POST consent/grant', (req) {
    sent = req.data;
    h.active = ['LOGIN'];
    return (201, {'purpose': 'LOGIN', 'granted_at': '2026-10-04T10:00:00Z', 'terms_version': 'v0', 'granted_by_guardian': false});
  });
  await h.openApp(tester);
  await h.openBiometrics(tester);
  expect(find.text('Autorize pelo menos um uso abaixo para cadastrar o rosto.'), findsOneWidget);

  await tester.tap(find.widgetWithText(SwitchListTile, 'Entrar no app com o rosto'));
  await tester.pumpAndSettle();
  expect(find.text('Termo do login facial.'), findsOneWidget);
  await tester.tap(find.text('Li e concordo'));
  await tester.pumpAndSettle();

  expect(sent, {'purpose': 'LOGIN', 'terms_version': 'v0', 'terms_hash': 'h0'});
  expect(find.text('Falta cadastrar o rosto para usar o que foi autorizado.'), findsOneWidget);
}

Future<void> _closingTermsDoesNotGrant(WidgetTester tester, BiometricsHarness h) async {
  await h.openApp(tester);
  await h.openBiometrics(tester);
  await tester.tap(find.widgetWithText(SwitchListTile, 'Catraca'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Agora não'));
  await tester.pumpAndSettle();
  expect(h.server.count('POST consent/grant'), 0);
}

Future<void> _outdatedTermsAskToReread(WidgetTester tester, BiometricsHarness h) async {
  h.server.on('POST consent/grant', (_) => (409, {'detail': 'terms_outdated'}));
  await h.openApp(tester);
  await h.openBiometrics(tester);
  await tester.tap(find.widgetWithText(SwitchListTile, 'Entrar no app com o rosto'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Li e concordo'));
  await tester.pumpAndSettle();
  expect(find.text('O termo foi atualizado. Leia a nova versão e autorize de novo.'), findsOneWidget);
}

Future<void> _revokeAsksConfirmation(WidgetTester tester, BiometricsHarness h) async {
  h.active = ['LOGIN', 'ACCESS'];
  Object? sent;
  h.server.on('POST consent/revoke', (req) {
    sent = req.data;
    h.active = ['LOGIN'];
    return (200, {'success': true, 'purge_scheduled_for': null});
  });
  await h.openApp(tester);
  await h.openBiometrics(tester);
  await tester.tap(find.widgetWithText(SwitchListTile, 'Catraca'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Revogar'));
  await tester.pumpAndSettle();
  expect(sent, {'purpose': 'ACCESS'});
  expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).value, isFalse);
}

Future<void> _enrollsWithTokenAndPhotoPerStep(WidgetTester tester, BiometricsHarness h) async {
  h.active = ['LOGIN'];
  Object? sent;
  String? authorization;
  h.server
    ..on('POST liveness/challenge', (req) {
      authorization = req.headers['Authorization'] as String?;
      return (
        201,
        {
          'challenge_id': 'c-1',
          'steps': ['CENTER', 'TURN_LEFT', 'TURN_RIGHT'],
          'expires_at': '2099-01-01T00:00:00Z',
        },
      );
    })
    ..on('POST me/enrollment', (req) {
      sent = req.data;
      h.enrolled = true;
      return (
        201,
        {
          'enrollment_status': 'h.active',
          'active_purposes': ['LOGIN'],
        },
      );
    });
  await h.openApp(tester);
  await h.openBiometrics(tester);
  await tester.tap(find.text('Cadastrar meu rosto'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Começar'));
  await tester.pumpAndSettle();

  expect(authorization, 'Bearer t-1');
  final body = sent! as FormData;
  expect(body.fields.single.value, 'c-1');
  expect(body.files.length, 3);
  expect(h.camera.isOpen, isFalse);
  expect(find.text('Rosto cadastrado.'), findsOneWidget);
  await tester.tap(find.text('Concluir'));
  await tester.pumpAndSettle();
  expect(find.text('Seu rosto está cadastrado.'), findsOneWidget);
}

Future<void> _badPhotoExplainsAndRetries(WidgetTester tester, BiometricsHarness h) async {
  h.active = ['LOGIN'];
  h.server
    ..on(
      'POST liveness/challenge',
      (_) => (
        201,
        {
          'challenge_id': 'c-1',
          'steps': ['CENTER', 'TURN_LEFT', 'TURN_RIGHT'],
        },
      ),
    )
    ..on('POST me/enrollment', (_) => (422, {'detail': 'quality:blur'}));
  await h.openApp(tester);
  await h.openBiometrics(tester);
  await tester.tap(find.text('Cadastrar meu rosto'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Começar'));
  await tester.pumpAndSettle();
  expect(find.textContaining('luz, enquadramento ou movimentos'), findsOneWidget);
  expect(find.text('Tentar de novo'), findsOneWidget);
}

Future<void> _under16CannotGrantAlone(WidgetTester tester, BiometricsHarness h) async {
  h.isAdult = false;
  h.decidesAlone = false;
  await h.openApp(tester);
  await h.openBiometrics(tester);
  expect(find.text('Até os 16 anos, quem autoriza é o seu responsável, pelo app dele.'), findsNWidgets(2));
  expect(find.text('Só para maiores de 18 anos.'), findsOneWidget);
  expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).onChanged, isNull);
}

Future<void> _teenGrantsLoginAndAccessNotAttendance(WidgetTester tester, BiometricsHarness h) async {
  h.isAdult = false;
  h.decidesAlone = true;
  await h.openApp(tester);
  await h.openBiometrics(tester);
  expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Entrar no app com o rosto')).onChanged, isNotNull);
  expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).onChanged, isNotNull);
  expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Presença em aula')).onChanged, isNull);
  expect(find.text('Só para maiores de 18 anos.'), findsOneWidget);
}

Future<void> _dependent16DecidesAlone(WidgetTester tester, BiometricsHarness h) async {
  h.server.on(
    'GET consent/dependents/s-1/status',
    (_) => (
      200,
      {'person_name': 'Bruno Souza', 'is_adult': false, 'decides_alone': true, 'active_purposes': <String>[], 'enrollment_status': 'none'},
    ),
  );
  await h.openApp(tester, role: 'guardian');
  await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Dependentes')));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Bruno Souza').first);
  await tester.pumpAndSettle();
  await tester.tap(find.text('Rosto'));
  await tester.pumpAndSettle();
  expect(find.text('A partir de 16 anos, o próprio aluno autoriza o uso do rosto pelo app.'), findsOneWidget);
  expect(find.byType(SwitchListTile), findsNothing);
}

Future<void> _guardianGrantsAccessForUnder16(WidgetTester tester, BiometricsHarness h) async {
  Object? sent;
  h.server
    ..on(
      'GET consent/dependents/s-1/status',
      (_) => (
        200,
        {'person_name': 'Bruno Souza', 'is_adult': false, 'decides_alone': false, 'active_purposes': h.active, 'enrollment_status': 'none'},
      ),
    )
    ..on('POST consent/dependents/s-1/grant', (req) {
      sent = req.data;
      h.active = ['ACCESS'];
      return (201, {'purpose': 'ACCESS', 'granted_at': '2026-10-04T10:00:00Z', 'terms_version': 'v0', 'granted_by_guardian': true});
    });
  await h.openApp(tester, role: 'guardian');
  await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Dependentes')));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Bruno Souza').first);
  await tester.pumpAndSettle();
  await tester.tap(find.text('Rosto'));
  await tester.pumpAndSettle();

  expect(find.widgetWithText(SwitchListTile, 'Presença em aula'), findsNothing);
  await tester.tap(find.widgetWithText(SwitchListTile, 'Catraca'));
  await tester.pumpAndSettle();
  expect(find.text('Autorização em nome de Bruno Souza'), findsOneWidget);
  await tester.tap(find.text('Li e concordo'));
  await tester.pumpAndSettle();
  expect(sent, {'purpose': 'ACCESS', 'terms_version': 'v0', 'terms_hash': 'h1'});
  expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).value, isTrue);
}

Future<void> _noPersonaNoFaceAnywhere(WidgetTester tester, BiometricsHarness h) async {
  await h.openApp(tester, persona: null, role: 'guardian');
  await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
  await tester.pumpAndSettle();
  expect(find.text('Reconhecimento facial'), findsNothing);
}
