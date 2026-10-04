import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:wedu_mobile/app.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/shared/cofre/cofre_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/shared/rosto/desafio.dart';
import 'package:wedu_mobile/shared/rosto/rosto_providers.dart';

import '../helpers/fakes.dart';

void main() {
  late ServidorFalso servidor;
  late TokenStoreEmMemoria tokens;
  late ContaLembradaEmMemoria contas;
  late CameraFalsa camera;

  setUpAll(() => initializeDateFormatting('pt_BR'));

  setUp(() {
    servidor = ServidorFalso();
    tokens = TokenStoreEmMemoria();
    contas = ContaLembradaEmMemoria();
    camera = CameraFalsa();
    servidor
      ..on('GET users/me', (_) => (200, usuarioJson()))
      ..on('GET institutions/current', (_) => (200, instituicaoJson()))
      ..on('GET access/me', (_) => (200, acessoJson()))
      ..on('GET sync/versions', (_) => (200, versoesJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}))
      ..on('GET school/my/agenda', (_) => (200, <Object>[]))
      ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
      ..on('POST liveness/login-challenge', (_) => (201, {
            'challenge_id': 'd-1', 'steps': ['TURN_RIGHT', 'CENTER', 'TURN_LEFT'], 'expires_at': '2099-01-01T00:00:00Z',
          }));
  });

  Future<void> abrirApp(WidgetTester tester, {String? persona = 'http://persona/api/v1/'}) async {
    await tester.pumpWidget(ProviderScope(
      retry: (_, _) => null,
      overrides: [
        tokenStoreProvider.overrideWithValue(tokens),
        httpAdapterProvider.overrideWithValue(servidor),
        cofreProvider.overrideWithValue(CofreEmMemoria()),
        cacheLocalProvider.overrideWithValue(CacheEmMemoria()),
        contaLembradaStoreProvider.overrideWithValue(contas),
        personaBaseUrlProvider.overrideWithValue(persona),
        capturaDeRostoProvider.overrideWithValue(camera),
        pausaEntrePassosProvider.overrideWithValue(Duration.zero),
      ],
      child: const WEduApp(),
    ));
    await tester.pumpAndSettle();
  }

  test('desafio na ordem sorteada pelo Persona', () {
    final desafio = Desafio.fromJson({'challenge_id': 'd', 'steps': ['TURN_LEFT', 'CENTER', 'TURN_RIGHT']});
    expect(desafio.passos, [PassoDesafio.esquerda, PassoDesafio.frente, PassoDesafio.direita]);
  });

  testWidgets('login com senha lembra a conta para o rosto', (tester) async {
    servidor.on('POST auth/login', (_) => (200, {'access_token': 't-1'}));
    await abrirApp(tester);
    expect(find.textContaining('Entrar com o rosto'), findsNothing);

    await tester.enterText(find.widgetWithText(TextFormField, 'E-mail'), 'ana@escola.example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Senha'), 'segredo123');
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();

    expect(contas.atual?.usuarioId, 'u-1');
    expect(contas.atual?.instituicaoId, 'i-1');
  });

  testWidgets('entra com o rosto: desafio, uma foto por passo, assertion e token', (tester) async {
    contas.atual = contaDaAna;
    Object? enviado;
    servidor
      ..on('POST auth/face/verify', (req) {
        enviado = req.data;
        return (200, {'assertion': 'assinado-pelo-persona'});
      })
      ..on('POST auth/facial-login', (req) => (200, {'access_token': req.data['assertion'] == 'assinado-pelo-persona' ? 't-rosto' : 'errado'}));
    await abrirApp(tester);

    await tester.tap(find.text('Entrar com o rosto como Ana'));
    await tester.pumpAndSettle();
    expect(find.text('Olá, Ana'), findsOneWidget);
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();

    final corpo = enviado! as FormData;
    expect({for (final campo in corpo.fields) campo.key: campo.value},
        {'wedu_user_id': 'u-1', 'institution_id': 'i-1', 'challenge_id': 'd-1'});
    expect(corpo.files.map((f) => f.key), ['frames', 'frames', 'frames']);
    expect(camera.fotos, 3);
    expect(camera.aberta, isFalse, reason: 'a câmera fecha depois do envio');
    expect(tokens.atual, 't-rosto');
    expect(find.text('Olá, Ana!'), findsOneWidget);
  });

  testWidgets('rosto recusado manda para a senha, sem dizer o motivo', (tester) async {
    contas.atual = contaDaAna;
    servidor.on('POST auth/face/verify', (_) => (401, {'detail': 'Não foi possível entrar com o rosto. Use a senha.'}));
    await abrirApp(tester);

    await tester.tap(find.text('Entrar com o rosto como Ana'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();

    expect(find.text('Não foi possível entrar com o rosto. Use a senha.'), findsOneWidget);
    expect(find.text('Tentar de novo'), findsOneWidget);
    expect(tokens.atual, isNull);
    await tester.tap(find.text('Entrar com a senha'));
    await tester.pumpAndSettle();
    expect(find.text('Entrar'), findsOneWidget);
  });

  testWidgets('sem permissão da câmera, avisa e oferece a senha', (tester) async {
    contas.atual = contaDaAna;
    camera = CameraFalsa(semPermissao: true);
    await abrirApp(tester);
    await tester.tap(find.text('Entrar com o rosto como Ana'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Começar'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Não foi possível abrir a câmera'), findsOneWidget);
    expect(servidor.contar('POST liveness/login-challenge'), 0);
  });

  testWidgets('sem o Persona configurado, só senha', (tester) async {
    contas.atual = contaDaAna;
    await abrirApp(tester, persona: null);
    expect(find.textContaining('Entrar com o rosto'), findsNothing);
  });

  testWidgets('usar outra conta esquece a conta lembrada', (tester) async {
    contas.atual = contaDaAna;
    await abrirApp(tester);
    await tester.tap(find.text('Não é Ana? Usar outra conta'));
    await tester.pumpAndSettle();
    expect(contas.atual, isNull);
    expect(find.textContaining('Entrar com o rosto'), findsNothing);
  });
}
