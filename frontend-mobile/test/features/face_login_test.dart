import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/shared/face/challenge.dart';
import 'package:wedu_mobile/shared/face/face_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';

import '../helpers/app_harness.dart';
import '../helpers/fakes.dart';

void main() {
  late FakeServer server;
  late InMemoryTokenStore tokens;
  late InMemoryRememberedAccountStore accounts;
  late FakeCamera camera;

  setUpAll(initializeDateFormatting);

  setUp(() {
    server = FakeServer();
    tokens = InMemoryTokenStore();
    accounts = InMemoryRememberedAccountStore();
    camera = FakeCamera();
    server
      ..on('GET users/me', (_) => (200, userJson()))
      ..on('GET institutions/current', (_) => (200, institutionJson()))
      ..on('GET access/me', (_) => (200, accessJson()))
      ..on('GET sync/versions', (_) => (200, versionsJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}))
      ..on('GET school/my/agenda', (_) => (200, <Object>[]))
      ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
      ..on(
        'POST liveness/login-challenge',
        (_) => (
          201,
          {
            'challenge_id': 'd-1',
            'steps': ['TURN_RIGHT', 'CENTER', 'TURN_LEFT'],
            'expires_at': '2099-01-01T00:00:00Z',
          },
        ),
      );
  });

  Future<void> openApp(WidgetTester tester, {String? persona = 'http://persona/api/v1/'}) => pumpWEduApp(tester, [
    tokenStoreProvider.overrideWithValue(tokens),
    httpAdapterProvider.overrideWithValue(server),
    fileVaultProvider.overrideWithValue(InMemoryVault()),
    localCacheProvider.overrideWithValue(InMemoryCache()),
    rememberedAccountStoreProvider.overrideWithValue(accounts),
    personaBaseUrlProvider.overrideWithValue(persona),
    faceCameraProvider.overrideWithValue(camera),
    stepPauseProvider.overrideWithValue(Duration.zero),
  ]);

  test('desafio na ordem sorteada pelo Persona', () {
    final challenge = Challenge.fromJson({
      'challenge_id': 'd',
      'steps': ['TURN_LEFT', 'CENTER', 'TURN_RIGHT'],
    });
    expect(challenge.steps, [ChallengeStep.turnLeft, ChallengeStep.center, ChallengeStep.turnRight]);
  });

  testWidgets('login com senha lembra a conta para o rosto', (tester) async {
    server.on('POST auth/login', (_) => (200, {'access_token': 't-1'}));
    await openApp(tester);
    expect(find.textContaining('Entrar com o rosto'), findsNothing);

    await tester.enterText(find.widgetWithText(TextFormField, 'E-mail'), 'ana@escola.example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Senha'), 'segredo123');
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();

    expect(accounts.current?.userId, 'u-1');
    expect(accounts.current?.institutionId, 'i-1');
  });

  testWidgets('entra com o rosto: desafio, uma foto por passo, assertion e token', (tester) async {
    accounts.current = anasAccount;
    Object? sent;
    server
      ..on('POST auth/face/verify', (req) {
        sent = req.data;
        return (200, {'assertion': 'signed-by-persona'});
      })
      ..on('POST auth/facial-login', (req) => (200, {'access_token': req.data['assertion'] == 'signed-by-persona' ? 't-face' : 'wrong'}));
    await openApp(tester);

    await tester.tap(find.text('Entrar com o rosto como Ana'));
    await tester.pumpAndSettle();
    expect(find.text('Olá, Ana'), findsOneWidget);
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();

    final body = sent! as FormData;
    expect(
      {for (final field in body.fields) field.key: field.value},
      {'wedu_user_id': 'u-1', 'institution_id': 'i-1', 'challenge_id': 'd-1'},
    );
    expect(body.files.map((f) => f.key), ['frames', 'frames', 'frames']);
    expect(camera.photos, 3);
    expect(camera.isOpen, isFalse, reason: 'a câmera fecha depois do envio');
    expect(tokens.current, 't-face');
    expect(find.text('Olá, Ana!'), findsOneWidget);
  });

  testWidgets('rosto recusado manda para a senha, sem dizer o motivo', (tester) async {
    accounts.current = anasAccount;
    server.on('POST auth/face/verify', (_) => (401, {'detail': 'Não foi possível entrar com o rosto. Use a senha.'}));
    await openApp(tester);

    await tester.tap(find.text('Entrar com o rosto como Ana'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();

    expect(find.text('Não foi possível entrar com o rosto. Use a senha.'), findsOneWidget);
    expect(find.text('Tentar de novo'), findsOneWidget);
    expect(tokens.current, isNull);
    await tester.tap(find.text('Entrar com a senha'));
    await tester.pumpAndSettle();
    expect(find.text('Entrar'), findsOneWidget);
  });

  testWidgets('sem permissão da câmera, avisa e oferece a senha', (tester) async {
    accounts.current = anasAccount;
    camera = FakeCamera(denied: true);
    await openApp(tester);
    await tester.tap(find.text('Entrar com o rosto como Ana'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Não foi possível abrir a câmera'), findsOneWidget);
    expect(server.count('POST liveness/login-challenge'), 0);
  });

  testWidgets('sem o Persona configurado, só senha', (tester) async {
    accounts.current = anasAccount;
    await openApp(tester, persona: null);
    expect(find.textContaining('Entrar com o rosto'), findsNothing);
  });

  testWidgets('usar outra conta esquece a conta lembrada', (tester) async {
    accounts.current = anasAccount;
    await openApp(tester);
    await tester.tap(find.text('Não é Ana? Usar outra conta'));
    await tester.pumpAndSettle();
    expect(accounts.current, isNull);
    expect(find.textContaining('Entrar com o rosto'), findsNothing);
  });
}
