import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:wedu_mobile/core/cache/local_cache.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';

import 'helpers/app_harness.dart';
import 'helpers/fakes.dart';

void main() {
  late FakeServer server;
  late InMemoryTokenStore tokens;
  late InMemoryCache cache;

  setUpAll(initializeDateFormatting);

  setUp(() {
    server = FakeServer();
    tokens = InMemoryTokenStore();
    cache = InMemoryCache();
    server
      ..on('GET sync/versions', (_) => (200, versionsJson()))
      ..on('GET institutions/current', (_) => (200, institutionJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 3, 'total': 5}))
      ..on('GET notifications/me', (_) => (200, [noticeJson('a1')]))
      ..on('GET school/my/agenda', (_) => (200, [agendaJson('ag1')]))
      ..on('GET assessment/my/report-card', (_) => (200, [reportCardJson()]))
      ..on('GET guardians/me/dependents', (_) => (200, [dependentJson()]))
      ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
      ..on('GET access/me', (_) => (200, accessJson()));
  });

  Future<void> openApp(WidgetTester tester, {Locale locale = const Locale('pt', 'BR')}) async {
    await pumpWEduApp(locale: locale, tester, [
      tokenStoreProvider.overrideWithValue(tokens),
      httpAdapterProvider.overrideWithValue(server),
      fileVaultProvider.overrideWithValue(InMemoryVault()),
      localCacheProvider.overrideWithValue(cache),
      rememberedAccountStoreProvider.overrideWithValue(InMemoryRememberedAccountStore()),
    ]);
  }

  Future<void> signIn(WidgetTester tester) async {
    await tester.enterText(find.widgetWithText(TextFormField, 'E-mail'), 'ana@escola.example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Senha'), 'segredo123');
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();
  }

  testWidgets('login recusado mostra a mensagem da API', (tester) async {
    server.on('POST auth/login', (_) => (401, {'detail': 'E-mail ou senha incorretos'}));
    await openApp(tester);

    await signIn(tester);

    expect(find.text('E-mail ou senha incorretos'), findsOneWidget);
    expect(tokens.current, isNull);
  });

  testWidgets('aluno entra e vê as abas de aluno', (tester) async {
    server
      ..on('POST auth/login', (_) => (200, {'access_token': 't-1', 'token_type': 'bearer'}))
      ..on('GET users/me', (_) => (200, userJson()));
    await openApp(tester);

    await signIn(tester);

    expect(tokens.current, 't-1');
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Boletim'), findsOneWidget);
    expect(find.text('Dependentes'), findsNothing);
  });

  testWidgets('responsável com sessão salva vê os dependentes', (tester) async {
    tokens.current = 't-1';
    server.on('GET users/me', (_) => (200, userJson(role: 'guardian')));
    await openApp(tester);

    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Boletim'), findsNothing);
    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Dependentes')));
    await tester.pumpAndSettle();
    expect(find.text('Bruno Souza'), findsWidgets);
  });

  testWidgets('token expirado volta para o login', (tester) async {
    tokens.current = 'vencido';
    server.on('GET users/me', (_) => (401, {'detail': 'Token inválido'}));
    await openApp(tester);

    expect(find.text('Entrar'), findsOneWidget);
    expect(tokens.current, isNull);
  });

  testWidgets('sem rede, abre com a sessão e as telas salvas', (tester) async {
    tokens.current = 't-1';
    const owner = 'i-1_u-1';
    await cache.save('session', CacheEntry(null, {'user': userJson(), 'institution': institutionJson()}));
    await cache.save('$owner/notices_summary', const CacheEntry(1, {'unread': 2, 'total': 2}));
    await cache.save('$owner/agenda', CacheEntry(1, [agendaJson('ag1')]));
    for (final route in [
      'GET users/me',
      'GET institutions/current',
      'GET sync/versions',
      'GET notifications/me/summary',
      'GET school/my/agenda',
    ]) {
      server.on(route, (req) => throw offline(req));
    }
    await openApp(tester);

    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('2 sem ler'), findsOneWidget);
    expect(find.textContaining('Prova bimestral'), findsOneWidget);
  });

  testWidgets('versão igual à salva não baixa a tela de novo', (tester) async {
    tokens.current = 't-1';
    server.on('GET users/me', (_) => (200, userJson()));
    await cache.save('i-1_u-1/agenda', CacheEntry(1, [agendaJson('ag1')]));
    await openApp(tester);

    expect(find.textContaining('Prova bimestral'), findsOneWidget);
    expect(server.count('GET school/my/agenda'), 0);
    expect(server.count('GET notifications/me/summary'), 1);
  });

  testWidgets('sair apaga o cache da conta', (tester) async {
    tokens.current = 't-1';
    server.on('GET users/me', (_) => (200, userJson()));
    await openApp(tester);
    expect(cache.entries, isNotEmpty);

    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sair'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sair').last);
    await tester.pumpAndSettle();

    expect(find.text('Entrar'), findsOneWidget);
    expect(cache.entries, isEmpty);
    expect(tokens.current, isNull);
  });

  testWidgets('sessão salva com token recusado volta ao login e apaga o cache', (tester) async {
    tokens.current = 'vencido';
    await cache.save('session', CacheEntry(null, {'user': userJson(), 'institution': institutionJson()}));
    for (final route in ['GET users/me', 'GET sync/versions', 'GET notifications/me/summary', 'GET school/my/agenda']) {
      server.on(route, (_) => (401, {'detail': 'Token inválido'}));
    }
    await openApp(tester);

    expect(find.text('Entrar'), findsOneWidget);
    expect(tokens.current, isNull);
    expect(cache.entries, isEmpty);
  });

  testWidgets('aluno abre o QR do benefício liberado, mesmo sem rede', (tester) async {
    tokens.current = 't-1';
    await cache.save('session', CacheEntry(null, {'user': userJson(), 'institution': institutionJson()}));
    await cache.save(
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
      server.on(route, (req) => throw offline(req));
    }
    await openApp(tester);

    expect(find.text('1 para retirar'), findsOneWidget);
    await tester.tap(find.text('Benefícios'));
    await tester.pumpAndSettle();
    expect(find.text('Retirado'), findsOneWidget);
    expect(find.text('Material'), findsOneWidget);
    await tester.tap(find.text('Mostrar QR'));
    await tester.pumpAndSettle();
    expect(find.byType(QrImageView), findsOneWidget);
    expect(find.text('COD1'), findsOneWidget);
  });

  testWidgets('sem benefício liberado, o início não mostra o cartão', (tester) async {
    tokens.current = 't-1';
    server.on('GET users/me', (_) => (200, userJson()));
    await openApp(tester);
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Benefícios'), findsNothing);
  });

  testWidgets('professor abre o QR de retirada da requisição aprovada, mesmo sem rede', (tester) async {
    tokens.current = 't-1';
    await cache.save(
      'session',
      CacheEntry(null, {
        'user': userJson(role: 'instructor'),
        'institution': institutionJson(),
        'access': accessJson(permissions: ['warehouse.request']),
      }),
    );
    await cache.save(
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
      server.on(route, (req) => throw offline(req));
    }
    await openApp(tester);

    expect(find.text('1 para retirar'), findsOneWidget);
    await tester.tap(find.text('Requisições de material'));
    await tester.pumpAndSettle();
    expect(find.text('Aguardando aprovação'), findsOneWidget);
    await tester.tap(find.text('QR de retirada'));
    await tester.pumpAndSettle();
    expect(find.byType(QrImageView), findsOneWidget);
    expect(find.text('RET123'), findsOneWidget);
  });

  testWidgets('sem permissão de requisitar, o início não mostra materiais', (tester) async {
    tokens.current = 't-1';
    server.on('GET users/me', (_) => (200, userJson()));
    await openApp(tester);
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Requisições de material'), findsNothing);
  });

  testWidgets('em inglês, a tela segue o idioma', (tester) async {
    tokens.current = 't-1';
    server.on('GET users/me', (_) => (200, userJson()));
    await openApp(tester, locale: const Locale('en'));

    expect(find.text('Hi, Ana!'), findsOneWidget);
    expect(find.text('Report card'), findsOneWidget);
    expect(find.text('Boletim'), findsNothing);
  });
}
