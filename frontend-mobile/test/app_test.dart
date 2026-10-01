import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:wedu_mobile/app.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';

import 'helpers/fakes.dart';

void main() {
  late ServidorFalso servidor;
  late TokenStoreEmMemoria tokens;

  setUpAll(() => initializeDateFormatting('pt_BR'));

  setUp(() {
    servidor = ServidorFalso();
    tokens = TokenStoreEmMemoria();
    servidor
      ..on('GET institutions/current', (_) => (200, instituicaoJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 3, 'total': 5}))
      ..on('GET notifications/me', (_) => (200, [avisoJson('a1')]))
      ..on('GET school/my/agenda', (_) => (200, [agendaJson('ag1')]))
      ..on('GET assessment/my/report-card', (_) => (200, [boletimJson()]))
      ..on('GET guardians/me/dependents', (_) => (200, [dependenteJson()]));
  });

  Future<void> abrirApp(WidgetTester tester) async {
    await tester.pumpWidget(ProviderScope(
      retry: (_, _) => null,
      overrides: [
        tokenStoreProvider.overrideWithValue(tokens),
        httpAdapterProvider.overrideWithValue(servidor),
      ],
      child: const WEduApp(),
    ));
    await tester.pumpAndSettle();
  }

  Future<void> entrar(WidgetTester tester) async {
    await tester.enterText(find.widgetWithText(TextFormField, 'E-mail'), 'ana@escola.example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Senha'), 'segredo123');
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();
  }

  testWidgets('login recusado mostra a mensagem da API', (tester) async {
    servidor.on('POST auth/login', (_) => (401, {'detail': 'E-mail ou senha incorretos'}));
    await abrirApp(tester);

    await entrar(tester);

    expect(find.text('E-mail ou senha incorretos'), findsOneWidget);
    expect(tokens.atual, isNull);
  });

  testWidgets('aluno entra e vê as abas de aluno', (tester) async {
    servidor
      ..on('POST auth/login', (_) => (200, {'access_token': 't-1', 'token_type': 'bearer'}))
      ..on('GET users/me', (_) => (200, usuarioJson()));
    await abrirApp(tester);

    await entrar(tester);

    expect(tokens.atual, 't-1');
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Boletim'), findsOneWidget);
    expect(find.text('Dependentes'), findsNothing);
  });

  testWidgets('responsável com sessão salva vê os dependentes', (tester) async {
    tokens.atual = 't-1';
    servidor.on('GET users/me', (_) => (200, usuarioJson(role: 'guardian')));
    await abrirApp(tester);

    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Boletim'), findsNothing);
    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Dependentes')));
    await tester.pumpAndSettle();
    expect(find.text('Bruno Souza'), findsWidgets);
  });

  testWidgets('token expirado volta para o login', (tester) async {
    tokens.atual = 'vencido';
    servidor.on('GET users/me', (_) => (401, {'detail': 'Token inválido'}));
    await abrirApp(tester);

    expect(find.text('Entrar'), findsOneWidget);
    expect(tokens.atual, isNull);
  });
}
