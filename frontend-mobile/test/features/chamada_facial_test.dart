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
import 'package:wedu_mobile/features/chamada_facial/chamada_facial_providers.dart';
import 'package:wedu_mobile/shared/rosto/rosto_providers.dart';

import '../helpers/fakes.dart';

void main() {
  late ServidorFalso servidor;
  late CameraFalsa camera;
  late int consultas;
  late CofreEmMemoria cofre;
  late CacheEmMemoria cache;
  late bool semInternet;

  setUpAll(() => initializeDateFormatting('pt_BR'));

  Map<String, dynamic> pessoa(String id, String nome, {String? recorte, String? cadastro}) =>
      {'person_id': id, 'name': nome, 'score': 0.5, 'confirmed_angles': <String>[], 'crop_url': recorte, 'enrollment_photo_url': cadastro};

  setUp(() {
    servidor = ServidorFalso();
    camera = CameraFalsa();
    consultas = 0;
    cofre = CofreEmMemoria();
    cache = CacheEmMemoria();
    semInternet = false;
    servidor
      ..on('GET users/me', (_) => (200, usuarioJson(role: 'instructor')))
      ..on('GET institutions/current', (_) => (200, instituicaoJson()))
      ..on('GET access/me', (_) => (200, acessoJson(permissoes: ['teaching.access'])))
      ..on('GET sync/versions', (_) => (200, versoesJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}))
      ..on('GET assessment/teaching/offerings', (_) => (200, [{'id': 't-1', 'name': 'Matemática 6A'}]))
      ..on('GET schedule/classes/t-1/meetings', (_) => (200, [
            {'id': 'e-1', 'title': 'Aula de hoje', 'starts_at': DateTime.now().toUtc().toIso8601String(), 'is_closed': false},
            {'id': 'e-0', 'title': 'Aula encerrada', 'starts_at': '2026-01-01T10:00:00Z', 'is_closed': true},
          ]))
      ..on('POST sessions', (req) => semInternet ? throw semRede(req) : (201, {'session_id': 's-1', 'status': 'OPEN', 'students_with_consent': 3, 'students_without_consent': 1}))
      ..on('POST sessions/s-1/images', (req) => semInternet ? throw semRede(req) : (202, {'image_id': 'i-1', 'task_id': 'k'}))
      ..on('GET sessions/s-1/result', (_) {
        consultas++;
        return (200, {
          'status': 'AWAITING_REVIEW',
          'present': [pessoa('p-ana', 'Ana')],
          'uncertain': [pessoa('p-beto', 'Beto', recorte: '/api/v1/sessions/s-1/detections/d-1/crop', cadastro: '/api/v1/sessions/s-1/people/p-beto/enrollment-photo')],
          'absent': [pessoa('p-caio', 'Caio')],
          'without_consent': [pessoa('p-duda', 'Duda')],
          'metrics': {'faces_detected': 3, 'faces_discarded_quality': 0},
          'images_pending': consultas < 2 ? 1 : 0,
        });
      })
      ..on('GET /api/v1/sessions/s-1/detections/d-1/crop', (_) => (200, 'jpg'))
      ..on('GET /api/v1/sessions/s-1/people/p-beto/enrollment-photo', (_) => (200, 'jpg'));
  });

  Future<void> abrirApp(WidgetTester tester, {String? persona = 'http://persona/api/v1/'}) async {
    // Tela de celular em pé: a revisão inteira cabe sem rolar.
    tester.view.physicalSize = const Size(800, 1800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(ProviderScope(
      retry: (_, _) => null,
      overrides: [
        tokenStoreProvider.overrideWithValue(TokenStoreEmMemoria('t-prof')),
        httpAdapterProvider.overrideWithValue(servidor),
        cofreProvider.overrideWithValue(cofre),
        cacheLocalProvider.overrideWithValue(cache),
        contaLembradaStoreProvider.overrideWithValue(ContaLembradaEmMemoria()),
        personaBaseUrlProvider.overrideWithValue(persona),
        cameraDeSalaProvider.overrideWithValue(camera),
        intervaloDoResultadoProvider.overrideWithValue(Duration.zero),
      ],
      child: const WEduApp(),
    ));
    await tester.pumpAndSettle();
  }

  Future<void> abrirEncontro(WidgetTester tester) async {
    await tester.tap(find.text('Chamada facial'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Matemática 6A'));
    await tester.pumpAndSettle();
    expect(find.text('Aula encerrada'), findsNothing);
    await tester.tap(find.text('Aula de hoje'));
    await tester.pumpAndSettle();
  }

  testWidgets('professor fotografa a sala, revisa e confirma a chamada', (tester) async {
    Object? aberta;
    Object? foto;
    Object? confirmada;
    servidor
      ..on('POST sessions', (req) {
        aberta = req.data;
        return (201, {'session_id': 's-1', 'status': 'OPEN', 'students_with_consent': 3, 'students_without_consent': 1});
      })
      ..on('POST sessions/s-1/images', (req) {
        foto = req.data;
        return (202, {'image_id': 'i-1', 'task_id': 'k'});
      })
      ..on('POST sessions/s-1/confirm', (req) {
        confirmada = req.data;
        return (200, {'session_id': 's-1', 'status': 'CONFIRMED', 'records_saved': 4});
      });
    await abrirApp(tester);
    await abrirEncontro(tester);

    expect(aberta, {'wedu_class_offering_id': 't-1', 'wedu_meeting_id': 'e-1'});
    expect(find.textContaining('3 aluno(s) com reconhecimento autorizado'), findsOneWidget);
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    final corpo = foto! as FormData;
    expect(corpo.fields.firstWhere((c) => c.key == 'angle').value, 'CENTER');
    expect(corpo.files.single.key, 'file');

    await tester.tap(find.text('Analisar 1 foto(s)'));
    await tester.pumpAndSettle();
    expect(consultas, 2, reason: 'espera o Persona processar a foto pendente');
    expect(camera.aberta, isFalse);
    expect(find.text('Conferir (1)'), findsOneWidget);
    expect(find.text('Na foto'), findsOneWidget);
    expect(find.text('Cadastro'), findsOneWidget);
    expect(find.text('Confirmar chamada: 1 presente(s) de 4'), findsOneWidget);

    await tester.tap(find.widgetWithText(CheckboxListTile, 'Beto'));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(CheckboxListTile, 'Duda'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar chamada: 3 presente(s) de 4'));
    await tester.pumpAndSettle();

    final enviado = confirmada! as Map<String, dynamic>;
    expect((enviado['present'] as List).toSet(), {'p-ana', 'p-beto', 'p-duda'});
    expect((enviado['absent'] as List).toSet(), {'p-caio'});
    expect(find.text('Chamada registrada: 3 presente(s) de 4.'), findsOneWidget);
  });

  testWidgets('turma que não ministra: avisa', (tester) async {
    servidor.on('POST sessions', (_) => (403, {'detail': 'professor não ministra esta turma no W-Edu'}));
    await abrirApp(tester);
    await abrirEncontro(tester);
    expect(find.text('Você não ministra esta turma.'), findsOneWidget);
  });

  testWidgets('falha ao confirmar mantém a revisão', (tester) async {
    servidor.on('POST sessions/s-1/confirm', (_) => (409, {'detail': 'present + absent precisa cobrir exatamente os matriculados ativos'}));
    await abrirApp(tester);
    await abrirEncontro(tester);
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Analisar 1 foto(s)'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar chamada: 1 presente(s) de 4'));
    await tester.pumpAndSettle();
    expect(find.textContaining('matriculados ativos'), findsOneWidget);
    expect(find.text('Confirmar chamada: 1 presente(s) de 4'), findsOneWidget);
  });

  testWidgets('sem o Persona, sem chamada facial', (tester) async {
    await abrirApp(tester, persona: null);
    expect(find.text('Chamada facial'), findsNothing);
  });

  testWidgets('sem internet: fotografa, guarda cifrado e envia quando a rede volta', (tester) async {
    semInternet = true;
    final fotos = <FormData>[];
    Object? confirmada;
    servidor
      ..on('POST sessions/s-1/images', (req) {
        if (semInternet) throw semRede(req);
        fotos.add(req.data as FormData);
        return (202, {'image_id': 'i', 'task_id': 'k'});
      })
      ..on('POST sessions/s-1/confirm', (req) {
        confirmada = req.data;
        return (200, {'session_id': 's-1', 'status': 'CONFIRMED', 'records_saved': 4});
      });
    await abrirApp(tester);
    await abrirEncontro(tester);

    expect(find.textContaining('Sem internet agora'), findsOneWidget);
    await tester.tap(find.text('Fotografar e enviar depois'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Lado esquerdo'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Guardar 2 foto(s)'));
    await tester.pumpAndSettle();
    expect(find.textContaining('2 foto(s) guardada(s)'), findsOneWidget);
    expect(cofre.arquivos.keys.where((nome) => nome.startsWith('chamada_')), hasLength(2));
    expect(servidor.contar('POST sessions/s-1/images'), 0);
    expect(camera.aberta, isFalse);

    // A rede volta: ao abrir a chamada facial, o app envia sozinho e a chamada fica pronta para revisar.
    semInternet = false;
    await tester.tap(find.text('Voltar aos encontros'));
    await tester.pumpAndSettle();
    expect(find.textContaining('pronta para revisar'), findsOneWidget);
    expect(fotos.map((f) => f.fields.firstWhere((c) => c.key == 'angle').value).toSet(), {'LEFT', 'CENTER'});
    expect(fotos.every((f) => f.fields.any((c) => c.key == 'captured_at')), isTrue);

    await tester.tap(find.textContaining('Matemática 6A · Aula de hoje'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar chamada: 1 presente(s) de 4'));
    await tester.pumpAndSettle();
    expect((confirmada! as Map<String, dynamic>)['present'], ['p-ana']);
    expect(cofre.arquivos.keys.where((nome) => nome.startsWith('chamada_')), isEmpty, reason: 'confirmada, as fotos somem do aparelho');
  });

  testWidgets('turmas e encontros abrem do cache sem internet', (tester) async {
    await abrirApp(tester);
    await abrirEncontro(tester);

    // Outra abertura do app, agora sem rede: lista do cache.
    for (final rota in ['GET users/me', 'GET institutions/current', 'GET access/me', 'GET sync/versions', 'GET assessment/teaching/offerings', 'GET schedule/classes/t-1/meetings']) {
      servidor.on(rota, (req) => throw semRede(req));
    }
    await tester.pumpWidget(const SizedBox());
    await abrirApp(tester);
    await tester.tap(find.text('Chamada facial'));
    await tester.pumpAndSettle();
    expect(find.text('Matemática 6A'), findsOneWidget);
    await tester.tap(find.text('Matemática 6A'));
    await tester.pumpAndSettle();
    expect(find.text('Aula de hoje'), findsOneWidget);
  });

  testWidgets('sair avisa e apaga as fotos não enviadas', (tester) async {
    semInternet = true;
    await abrirApp(tester);
    await abrirEncontro(tester);
    await tester.tap(find.text('Fotografar e enviar depois'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Guardar 1 foto(s)'));
    await tester.pumpAndSettle();

    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sair'));
    await tester.pumpAndSettle();
    expect(find.textContaining('1 chamada(s) com fotos ainda não enviadas'), findsOneWidget);
    await tester.tap(find.text('Sair').last);
    await tester.pumpAndSettle();
    expect(cofre.arquivos, isEmpty);
  });
}
