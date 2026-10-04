import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/features/attendance/attendance_flow.dart';
import 'package:wedu_mobile/shared/face/face_providers.dart';

import '../helpers/app_harness.dart';
import '../helpers/fakes.dart';

void main() {
  late FakeServer server;
  late FakeCamera camera;
  late int polls;
  late InMemoryVault vault;
  late InMemoryCache cache;
  late bool noInternet;

  setUpAll(initializeDateFormatting);

  Map<String, dynamic> person(String id, String name, {String? crop, String? enrollment}) => {
    'person_id': id,
    'name': name,
    'score': 0.5,
    'confirmed_angles': <String>[],
    'crop_url': crop,
    'enrollment_photo_url': enrollment,
  };

  setUp(() {
    server = FakeServer();
    camera = FakeCamera();
    polls = 0;
    vault = InMemoryVault();
    cache = InMemoryCache();
    noInternet = false;
    server
      ..on('GET users/me', (_) => (200, userJson(role: 'instructor')))
      ..on('GET institutions/current', (_) => (200, institutionJson()))
      ..on('GET access/me', (_) => (200, accessJson(permissions: ['teaching.access'])))
      ..on('GET sync/versions', (_) => (200, versionsJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}))
      ..on(
        'GET assessment/teaching/offerings',
        (_) => (
          200,
          [
            {'id': 't-1', 'name': 'Matemática 6A'},
          ],
        ),
      )
      ..on(
        'GET schedule/classes/t-1/meetings',
        (_) => (
          200,
          [
            {'id': 'e-1', 'title': 'Aula de hoje', 'starts_at': DateTime.now().toUtc().toIso8601String(), 'is_closed': false},
            {'id': 'e-0', 'title': 'Aula encerrada', 'starts_at': '2026-01-01T10:00:00Z', 'is_closed': true},
          ],
        ),
      )
      ..on(
        'POST sessions',
        (req) => noInternet
            ? throw offline(req)
            : (201, {'session_id': 's-1', 'status': 'OPEN', 'students_with_consent': 3, 'students_without_consent': 1}),
      )
      ..on('POST sessions/s-1/images', (req) => noInternet ? throw offline(req) : (202, {'image_id': 'i-1', 'task_id': 'k'}))
      ..on('GET sessions/s-1/result', (_) {
        polls++;
        return (
          200,
          {
            'status': 'AWAITING_REVIEW',
            'present': [person('p-ana', 'Ana')],
            'uncertain': [
              person(
                'p-beto',
                'Beto',
                crop: '/api/v1/sessions/s-1/detections/d-1/crop',
                enrollment: '/api/v1/sessions/s-1/people/p-beto/enrollment-photo',
              ),
            ],
            'absent': [person('p-caio', 'Caio')],
            'without_consent': [person('p-duda', 'Duda')],
            'metrics': {'faces_detected': 3, 'faces_discarded_quality': 0},
            'images_pending': polls < 2 ? 1 : 0,
          },
        );
      })
      ..on('GET /api/v1/sessions/s-1/detections/d-1/crop', (_) => (200, 'jpg'))
      ..on('GET /api/v1/sessions/s-1/people/p-beto/enrollment-photo', (_) => (200, 'jpg'));
  });

  Future<void> openApp(WidgetTester tester, {String? persona = 'http://persona/api/v1/'}) async {
    // Tela de celular em pé: a revisão inteira cabe sem rolar.
    tester.view.physicalSize = const Size(800, 1800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await pumpWEduApp(tester, [
      tokenStoreProvider.overrideWithValue(InMemoryTokenStore('t-prof')),
      httpAdapterProvider.overrideWithValue(server),
      fileVaultProvider.overrideWithValue(vault),
      localCacheProvider.overrideWithValue(cache),
      rememberedAccountStoreProvider.overrideWithValue(InMemoryRememberedAccountStore()),
      personaBaseUrlProvider.overrideWithValue(persona),
      roomCameraProvider.overrideWithValue(camera),
      resultPollIntervalProvider.overrideWithValue(Duration.zero),
    ]);
  }

  Future<void> openMeeting(WidgetTester tester) async {
    await tester.tap(find.text('Chamada facial'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Matemática 6A'));
    await tester.pumpAndSettle();
    expect(find.text('Aula encerrada'), findsNothing);
    await tester.tap(find.text('Aula de hoje'));
    await tester.pumpAndSettle();
  }

  testWidgets('professor fotografa a sala, revisa e confirma a chamada', (tester) async {
    Object? opened;
    Object? photo;
    Object? confirmed;
    server
      ..on('POST sessions', (req) {
        opened = req.data;
        return (201, {'session_id': 's-1', 'status': 'OPEN', 'students_with_consent': 3, 'students_without_consent': 1});
      })
      ..on('POST sessions/s-1/images', (req) {
        photo = req.data;
        return (202, {'image_id': 'i-1', 'task_id': 'k'});
      })
      ..on('POST sessions/s-1/confirm', (req) {
        confirmed = req.data;
        return (200, {'session_id': 's-1', 'status': 'CONFIRMED', 'records_saved': 4});
      });
    await openApp(tester);
    await openMeeting(tester);

    expect(opened, {'wedu_class_offering_id': 't-1', 'wedu_meeting_id': 'e-1'});
    expect(find.textContaining('3 aluno(s) com reconhecimento autorizado'), findsOneWidget);
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    final body = photo! as FormData;
    expect(body.fields.firstWhere((c) => c.key == 'angle').value, 'CENTER');
    expect(body.files.single.key, 'file');

    await tester.tap(find.text('Analisar 1 foto'));
    await tester.pumpAndSettle();
    expect(polls, 2, reason: 'espera o Persona processar a foto pendente');
    expect(camera.isOpen, isFalse);
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

    final confirmedBody = confirmed! as Map<String, dynamic>;
    expect((confirmedBody['present'] as List).toSet(), {'p-ana', 'p-beto', 'p-duda'});
    expect((confirmedBody['absent'] as List).toSet(), {'p-caio'});
    expect(find.text('Chamada registrada: 3 presente(s) de 4.'), findsOneWidget);
  });

  testWidgets('turma que não ministra: avisa', (tester) async {
    server.on('POST sessions', (_) => (403, {'detail': 'professor não ministra esta turma no W-Edu'}));
    await openApp(tester);
    await openMeeting(tester);
    expect(find.text('Você não ministra esta turma.'), findsOneWidget);
  });

  testWidgets('falha ao confirmar mantém a revisão', (tester) async {
    server.on('POST sessions/s-1/confirm', (_) => (409, {'detail': 'present + absent precisa cobrir exatamente os matriculados ativos'}));
    await openApp(tester);
    await openMeeting(tester);
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Analisar 1 foto'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar chamada: 1 presente(s) de 4'));
    await tester.pumpAndSettle();
    expect(find.textContaining('matriculados ativos'), findsOneWidget);
    expect(find.text('Confirmar chamada: 1 presente(s) de 4'), findsOneWidget);
  });

  testWidgets('sem o Persona, sem chamada facial', (tester) async {
    await openApp(tester, persona: null);
    expect(find.text('Chamada facial'), findsNothing);
  });

  testWidgets('sem internet: fotografa, guarda cifrado e envia quando a rede volta', (tester) async {
    noInternet = true;
    final photos = <FormData>[];
    Object? confirmed;
    server
      ..on('POST sessions/s-1/images', (req) {
        if (noInternet) throw offline(req);
        photos.add(req.data as FormData);
        return (202, {'image_id': 'i', 'task_id': 'k'});
      })
      ..on('POST sessions/s-1/confirm', (req) {
        confirmed = req.data;
        return (200, {'session_id': 's-1', 'status': 'CONFIRMED', 'records_saved': 4});
      });
    await openApp(tester);
    await openMeeting(tester);

    expect(find.textContaining('Sem internet agora'), findsOneWidget);
    await tester.tap(find.text('Fotografar e enviar depois'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Lado esquerdo'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Guardar 2 fotos'));
    await tester.pumpAndSettle();
    expect(find.textContaining('2 fotos guardadas'), findsOneWidget);
    expect(vault.files.keys.where((name) => name.startsWith('attendance_')), hasLength(2));
    expect(server.count('POST sessions/s-1/images'), 0);
    expect(camera.isOpen, isFalse);

    // A rede volta: ao abrir a chamada facial, o app envia sozinho e a chamada fica pronta para revisar.
    noInternet = false;
    await tester.tap(find.text('Voltar aos encontros'));
    await tester.pumpAndSettle();
    expect(find.textContaining('pronta para revisar'), findsOneWidget);
    expect(photos.map((f) => f.fields.firstWhere((c) => c.key == 'angle').value).toSet(), {'LEFT', 'CENTER'});
    expect(photos.every((f) => f.fields.any((c) => c.key == 'captured_at')), isTrue);

    await tester.tap(find.textContaining('Matemática 6A · Aula de hoje'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar chamada: 1 presente(s) de 4'));
    await tester.pumpAndSettle();
    expect((confirmed! as Map<String, dynamic>)['present'], ['p-ana']);
    expect(vault.files.keys.where((name) => name.startsWith('attendance_')), isEmpty, reason: 'confirmada, as fotos somem do aparelho');
  });

  testWidgets('turmas e encontros abrem do cache sem internet', (tester) async {
    await openApp(tester);
    await openMeeting(tester);

    // Outra abertura do app, agora sem rede: lista do cache.
    for (final route in [
      'GET users/me',
      'GET institutions/current',
      'GET access/me',
      'GET sync/versions',
      'GET assessment/teaching/offerings',
      'GET schedule/classes/t-1/meetings',
    ]) {
      server.on(route, (req) => throw offline(req));
    }
    await tester.pumpWidget(const SizedBox());
    await openApp(tester);
    await tester.tap(find.text('Chamada facial'));
    await tester.pumpAndSettle();
    expect(find.text('Matemática 6A'), findsOneWidget);
    await tester.tap(find.text('Matemática 6A'));
    await tester.pumpAndSettle();
    expect(find.text('Aula de hoje'), findsOneWidget);
  });

  testWidgets('sair avisa e apaga as fotos não enviadas', (tester) async {
    noInternet = true;
    await openApp(tester);
    await openMeeting(tester);
    await tester.tap(find.text('Fotografar e enviar depois'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Centro'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Guardar 1 foto'));
    await tester.pumpAndSettle();

    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sair'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Há 1 chamada com fotos ainda não enviadas'), findsOneWidget);
    await tester.tap(find.text('Sair').last);
    await tester.pumpAndSettle();
    expect(vault.files, isEmpty);
  });
}
