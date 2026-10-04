import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/shared/face/face_providers.dart';

import '../helpers/app_harness.dart';
import '../helpers/fakes.dart';

void main() {
  late FakeServer server;
  late InMemoryTokenStore tokens;
  late FakeCamera camera;
  late List<String> active;
  late bool isAdult;
  late bool decidesAlone;
  late bool enrolled;

  setUpAll(initializeDateFormatting);

  Map<String, dynamic> status() => {
    'person_name': 'Ana Souza',
    'is_adult': isAdult,
    'decides_alone': decidesAlone,
    'active_purposes': active,
    'enrollment_status': enrolled ? 'active' : 'none',
  };

  setUp(() {
    server = FakeServer();
    tokens = InMemoryTokenStore('t-1');
    camera = FakeCamera();
    active = [];
    isAdult = true;
    decidesAlone = true;
    enrolled = false;
    server
      ..on('GET users/me', (_) => (200, userJson()))
      ..on('GET institutions/current', (_) => (200, institutionJson()))
      ..on('GET access/me', (_) => (200, accessJson()))
      ..on('GET sync/versions', (_) => (200, versionsJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}))
      ..on('GET school/my/agenda', (_) => (200, <Object>[]))
      ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
      ..on('GET guardians/me/dependents', (_) => (200, [dependentJson()]))
      ..on('GET consent/me/status', (req) => (req.headers['Authorization'] == 'Bearer t-1' ? 200 : 401, status()))
      ..on('GET consent/terms/LOGIN', (_) => (200, {'purpose': 'LOGIN', 'version': 'v0', 'text': 'Termo do login facial.', 'hash': 'h0'}))
      ..on('GET consent/terms/ACCESS', (_) => (200, {'purpose': 'ACCESS', 'version': 'v0', 'text': 'Termo da catraca.', 'hash': 'h1'}));
  });

  Future<void> openApp(WidgetTester tester, {String? persona = 'http://persona/api/v1/', String role = 'student'}) async {
    server.on('GET users/me', (_) => (200, userJson(role: role)));
    await pumpWEduApp(tester, [
      tokenStoreProvider.overrideWithValue(tokens),
      httpAdapterProvider.overrideWithValue(server),
      fileVaultProvider.overrideWithValue(InMemoryVault()),
      localCacheProvider.overrideWithValue(InMemoryCache()),
      rememberedAccountStoreProvider.overrideWithValue(InMemoryRememberedAccountStore()),
      personaBaseUrlProvider.overrideWithValue(persona),
      faceCameraProvider.overrideWithValue(camera),
      stepPauseProvider.overrideWithValue(Duration.zero),
    ]);
  }

  Future<void> openBiometrics(WidgetTester tester) async {
    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Reconhecimento facial'));
    await tester.pumpAndSettle();
  }

  testWidgets('adulto autoriza o login depois de ler o termo', (tester) async {
    Object? sent;
    server.on('POST consent/grant', (req) {
      sent = req.data;
      active = ['LOGIN'];
      return (201, {'purpose': 'LOGIN', 'granted_at': '2026-10-04T10:00:00Z', 'terms_version': 'v0', 'granted_by_guardian': false});
    });
    await openApp(tester);
    await openBiometrics(tester);
    expect(find.text('Autorize pelo menos um uso abaixo para cadastrar o rosto.'), findsOneWidget);

    await tester.tap(find.widgetWithText(SwitchListTile, 'Entrar no app com o rosto'));
    await tester.pumpAndSettle();
    expect(find.text('Termo do login facial.'), findsOneWidget);
    await tester.tap(find.text('Li e concordo'));
    await tester.pumpAndSettle();

    expect(sent, {'purpose': 'LOGIN', 'terms_version': 'v0', 'terms_hash': 'h0'});
    expect(find.text('Falta cadastrar o rosto para usar o que foi autorizado.'), findsOneWidget);
  });

  testWidgets('fechar o termo sem concordar não autoriza', (tester) async {
    await openApp(tester);
    await openBiometrics(tester);
    await tester.tap(find.widgetWithText(SwitchListTile, 'Catraca'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Agora não'));
    await tester.pumpAndSettle();
    expect(server.count('POST consent/grant'), 0);
  });

  testWidgets('termo desatualizado pede para ler de novo', (tester) async {
    server.on('POST consent/grant', (_) => (409, {'detail': 'terms_outdated'}));
    await openApp(tester);
    await openBiometrics(tester);
    await tester.tap(find.widgetWithText(SwitchListTile, 'Entrar no app com o rosto'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Li e concordo'));
    await tester.pumpAndSettle();
    expect(find.text('O termo foi atualizado. Leia a nova versão e autorize de novo.'), findsOneWidget);
  });

  testWidgets('revogar pede confirmação', (tester) async {
    active = ['LOGIN', 'ACCESS'];
    Object? sent;
    server.on('POST consent/revoke', (req) {
      sent = req.data;
      active = ['LOGIN'];
      return (200, {'success': true, 'purge_scheduled_for': null});
    });
    await openApp(tester);
    await openBiometrics(tester);
    await tester.tap(find.widgetWithText(SwitchListTile, 'Catraca'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Revogar'));
    await tester.pumpAndSettle();
    expect(sent, {'purpose': 'ACCESS'});
    expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).value, isFalse);
  });

  testWidgets('cadastra o rosto com o token do W-Edu e uma foto por passo', (tester) async {
    active = ['LOGIN'];
    Object? sent;
    String? authorization;
    server
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
        enrolled = true;
        return (
          201,
          {
            'enrollment_status': 'active',
            'active_purposes': ['LOGIN'],
          },
        );
      });
    await openApp(tester);
    await openBiometrics(tester);
    await tester.tap(find.text('Cadastrar meu rosto'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();

    expect(authorization, 'Bearer t-1');
    final body = sent! as FormData;
    expect(body.fields.single.value, 'c-1');
    expect(body.files.length, 3);
    expect(camera.isOpen, isFalse);
    expect(find.text('Rosto cadastrado.'), findsOneWidget);
    await tester.tap(find.text('Concluir'));
    await tester.pumpAndSettle();
    expect(find.text('Seu rosto está cadastrado.'), findsOneWidget);
  });

  testWidgets('foto ruim: explica e deixa tentar de novo', (tester) async {
    active = ['LOGIN'];
    server
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
    await openApp(tester);
    await openBiometrics(tester);
    await tester.tap(find.text('Cadastrar meu rosto'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();
    expect(find.textContaining('luz, enquadramento ou movimentos'), findsOneWidget);
    expect(find.text('Tentar de novo'), findsOneWidget);
  });

  testWidgets('menor de 16 não autoriza sozinho', (tester) async {
    isAdult = false;
    decidesAlone = false;
    await openApp(tester);
    await openBiometrics(tester);
    expect(find.text('Até os 16 anos, quem autoriza é o seu responsável, pelo app dele.'), findsNWidgets(2));
    expect(find.text('Só para maiores de 18 anos.'), findsOneWidget);
    expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).onChanged, isNull);
  });

  testWidgets('com 16 ou 17 anos autoriza login e catraca, mas não a presença', (tester) async {
    isAdult = false;
    decidesAlone = true;
    await openApp(tester);
    await openBiometrics(tester);
    expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Entrar no app com o rosto')).onChanged, isNotNull);
    expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Catraca')).onChanged, isNotNull);
    expect(tester.widget<SwitchListTile>(find.widgetWithText(SwitchListTile, 'Presença em aula')).onChanged, isNull);
    expect(find.text('Só para maiores de 18 anos.'), findsOneWidget);
  });

  testWidgets('dependente com 16 anos ou mais decide sozinho', (tester) async {
    server.on(
      'GET consent/dependents/s-1/status',
      (_) => (
        200,
        {
          'person_name': 'Bruno Souza',
          'is_adult': false,
          'decides_alone': true,
          'active_purposes': <String>[],
          'enrollment_status': 'none',
        },
      ),
    );
    await openApp(tester, role: 'guardian');
    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Dependentes')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Bruno Souza').first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Rosto'));
    await tester.pumpAndSettle();
    expect(find.text('A partir de 16 anos, o próprio aluno autoriza o uso do rosto pelo app.'), findsOneWidget);
    expect(find.byType(SwitchListTile), findsNothing);
  });

  testWidgets('responsável autoriza a catraca do dependente menor de 16', (tester) async {
    Object? sent;
    server
      ..on(
        'GET consent/dependents/s-1/status',
        (_) => (
          200,
          {'person_name': 'Bruno Souza', 'is_adult': false, 'decides_alone': false, 'active_purposes': active, 'enrollment_status': 'none'},
        ),
      )
      ..on('POST consent/dependents/s-1/grant', (req) {
        sent = req.data;
        active = ['ACCESS'];
        return (201, {'purpose': 'ACCESS', 'granted_at': '2026-10-04T10:00:00Z', 'terms_version': 'v0', 'granted_by_guardian': true});
      });
    await openApp(tester, role: 'guardian');
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
  });

  testWidgets('sem o Persona, nada de rosto no perfil nem no dependente', (tester) async {
    await openApp(tester, persona: null, role: 'guardian');
    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    expect(find.text('Reconhecimento facial'), findsNothing);
  });
}
