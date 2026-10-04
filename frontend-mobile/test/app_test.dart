import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:wedu_mobile/app.dart';
import 'package:wedu_mobile/core/cache/local_cache.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';

import 'helpers/fakes.dart';

void main() {
  late ServidorFalso servidor;
  late TokenStoreEmMemoria tokens;
  late CacheEmMemoria cache;

  setUpAll(() => initializeDateFormatting('pt_BR'));

  setUp(() {
    servidor = ServidorFalso();
    tokens = TokenStoreEmMemoria();
    cache = CacheEmMemoria();
    servidor
      ..on('GET sync/versions', (_) => (200, versoesJson()))
      ..on('GET institutions/current', (_) => (200, instituicaoJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 3, 'total': 5}))
      ..on('GET notifications/me', (_) => (200, [avisoJson('a1')]))
      ..on('GET school/my/agenda', (_) => (200, [agendaJson('ag1')]))
      ..on('GET assessment/my/report-card', (_) => (200, [boletimJson()]))
      ..on('GET guardians/me/dependents', (_) => (200, [dependenteJson()]))
      ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
      ..on('GET access/me', (_) => (200, acessoJson()));
  });

  Future<void> abrirApp(WidgetTester tester) async {
    await tester.pumpWidget(ProviderScope(
      retry: (_, _) => null,
      overrides: [
        tokenStoreProvider.overrideWithValue(tokens),
        httpAdapterProvider.overrideWithValue(servidor),
        cofreProvider.overrideWithValue(CofreEmMemoria()),
        cacheLocalProvider.overrideWithValue(cache),
        contaLembradaStoreProvider.overrideWithValue(ContaLembradaEmMemoria()),
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

  testWidgets('sem rede, abre com a sessão e as telas salvas', (tester) async {
    tokens.atual = 't-1';
    final dono = 'i-1_u-1';
    await cache.salvar('sessao', EntradaCache(null, {'usuario': usuarioJson(), 'instituicao': instituicaoJson()}));
    await cache.salvar('$dono/avisos_resumo', const EntradaCache(1, {'unread': 2, 'total': 2}));
    await cache.salvar('$dono/agenda', EntradaCache(1, [agendaJson('ag1')]));
    for (final rota in ['GET users/me', 'GET institutions/current', 'GET sync/versions', 'GET notifications/me/summary', 'GET school/my/agenda']) {
      servidor.on(rota, (req) => throw semRede(req));
    }
    await abrirApp(tester);

    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('2 sem ler'), findsOneWidget);
    expect(find.textContaining('Prova bimestral'), findsOneWidget);
  });

  testWidgets('versão igual à salva não baixa a tela de novo', (tester) async {
    tokens.atual = 't-1';
    servidor.on('GET users/me', (_) => (200, usuarioJson()));
    await cache.salvar('i-1_u-1/agenda', EntradaCache(1, [agendaJson('ag1')]));
    await abrirApp(tester);

    expect(find.textContaining('Prova bimestral'), findsOneWidget);
    expect(servidor.contar('GET school/my/agenda'), 0);
    expect(servidor.contar('GET notifications/me/summary'), 1);
  });

  testWidgets('sair apaga o cache da conta', (tester) async {
    tokens.atual = 't-1';
    servidor.on('GET users/me', (_) => (200, usuarioJson()));
    await abrirApp(tester);
    expect(cache.entradas, isNotEmpty);

    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sair'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sair').last);
    await tester.pumpAndSettle();

    expect(find.text('Entrar'), findsOneWidget);
    expect(cache.entradas, isEmpty);
    expect(tokens.atual, isNull);
  });

  testWidgets('sessão salva com token recusado volta ao login e apaga o cache', (tester) async {
    tokens.atual = 'vencido';
    await cache.salvar('sessao', EntradaCache(null, {'usuario': usuarioJson(), 'instituicao': instituicaoJson()}));
    for (final rota in ['GET users/me', 'GET sync/versions', 'GET notifications/me/summary', 'GET school/my/agenda']) {
      servidor.on(rota, (_) => (401, {'detail': 'Token inválido'}));
    }
    await abrirApp(tester);

    expect(find.text('Entrar'), findsOneWidget);
    expect(tokens.atual, isNull);
    expect(cache.entradas, isEmpty);
  });

  testWidgets('aluno abre o QR do benefício liberado, mesmo sem rede', (tester) async {
    tokens.atual = 't-1';
    await cache.salvar('sessao', EntradaCache(null, {'usuario': usuarioJson(), 'instituicao': instituicaoJson()}));
    await cache.salvar('i-1_u-1/beneficios', EntradaCache(1, [beneficioJson('1', validoAte: '2099-12-31'), beneficioJson('2', status: 'redeemed', item: 'Kit', tipo: 'material')]));
    for (final rota in ['GET users/me', 'GET institutions/current', 'GET sync/versions', 'GET notifications/me/summary', 'GET school/my/agenda', 'GET social/my/vouchers']) {
      servidor.on(rota, (req) => throw semRede(req));
    }
    await abrirApp(tester);

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
    tokens.atual = 't-1';
    servidor.on('GET users/me', (_) => (200, usuarioJson()));
    await abrirApp(tester);
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Benefícios'), findsNothing);
  });

  testWidgets('professor abre o QR de retirada da requisição aprovada, mesmo sem rede', (tester) async {
    tokens.atual = 't-1';
    await cache.salvar('sessao', EntradaCache(null, {
      'usuario': usuarioJson(role: 'instructor'),
      'instituicao': instituicaoJson(),
      'acesso': acessoJson(permissoes: ['warehouse.request']),
    }));
    await cache.salvar('i-1_u-1/requisicoes', EntradaCache(1, [requisicaoJson('r1', codigo: 'RET123'), requisicaoJson('r2', status: 'pending')]));
    for (final rota in ['GET users/me', 'GET institutions/current', 'GET access/me', 'GET sync/versions', 'GET notifications/me/summary', 'GET warehouse/my/requests']) {
      servidor.on(rota, (req) => throw semRede(req));
    }
    await abrirApp(tester);

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
    tokens.atual = 't-1';
    servidor.on('GET users/me', (_) => (200, usuarioJson()));
    await abrirApp(tester);
    expect(find.text('Olá, Ana!'), findsOneWidget);
    expect(find.text('Requisições de material'), findsNothing);
  });
}
