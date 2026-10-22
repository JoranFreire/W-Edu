import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/attendance/attendance_flow.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/shared/face/face_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';

import 'app_harness.dart';
import 'fakes.dart';

/// Professor com uma turma e o Persona respondendo uma chamada: 1 reconhecido, 1 para conferir,
/// 1 ausente e 1 sem autorização. `noInternet` derruba a abertura e o envio de fotos.
class AttendanceHarness {
  AttendanceHarness() {
    _registerUser();
    _registerTeaching();
    _registerPersona();
  }

  final server = FakeServer();
  final camera = FakeCamera();
  final vault = InMemoryVault();
  final cache = InMemoryCache();
  int polls = 0;
  bool noInternet = false;

  static Map<String, dynamic> person(String id, String name, {String? crop, String? enrollment}) => {
    'person_id': id,
    'name': name,
    'score': 0.5,
    'confirmed_angles': <String>[],
    'crop_url': crop,
    'enrollment_photo_url': enrollment,
  };

  void _registerUser() => server
    ..on('GET users/me', (_) => (200, userJson(role: 'instructor')))
    ..on('GET institutions/current', (_) => (200, institutionJson()))
    ..on('GET access/me', (_) => (200, accessJson(permissions: ['teaching.access'])))
    ..on('GET sync/versions', (_) => (200, versionsJson()))
    ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}));

  void _registerTeaching() => server
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
    );

  void _registerPersona() => server
    ..on(
      'POST sessions',
      (req) => noInternet
          ? throw offline(req)
          : (201, {'session_id': 's-1', 'status': 'OPEN', 'students_with_consent': 3, 'students_without_consent': 1}),
    )
    ..on('POST sessions/s-1/images', (req) => noInternet ? throw offline(req) : (202, {'image_id': 'i-1', 'task_id': 'k'}))
    ..on('GET sessions/s-1/result', (_) => (200, _result()))
    ..on('GET /api/v1/sessions/s-1/detections/d-1/crop', (_) => (200, 'jpg'))
    ..on('GET /api/v1/sessions/s-1/people/p-beto/enrollment-photo', (_) => (200, 'jpg'));

  Map<String, dynamic> _result() {
    polls++;
    return {
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
    };
  }

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

  /// Toca e espera a tela assentar.
  Future<void> tap(WidgetTester tester, Finder finder) async {
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }
}
