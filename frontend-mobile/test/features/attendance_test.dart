import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

import '../helpers/attendance_harness.dart';
import '../helpers/fakes.dart';

void main() {
  late AttendanceHarness h;

  setUpAll(initializeDateFormatting);
  setUp(() => h = AttendanceHarness());

  testWidgets('professor fotografa a sala, revisa e confirma a chamada', (tester) => _photographReviewAndConfirm(tester, h));
  testWidgets('turma que não ministra: avisa', (tester) => _notTheirClass(tester, h));
  testWidgets('falha ao confirmar mantém a revisão', (tester) => _confirmFailureKeepsReview(tester, h));
  testWidgets('sem o Persona, sem chamada facial', (tester) => _noPersonaNoAttendance(tester, h));
  testWidgets('sem internet: fotografa, guarda cifrado e envia quando a rede volta', (tester) => _offlinePhotosSyncLater(tester, h));
  testWidgets('turmas e encontros abrem do cache sem internet', (tester) => _offeringsFromCacheOffline(tester, h));
  testWidgets('sair avisa e apaga as fotos não enviadas', (tester) => _signOutWarnsAndDeletesPhotos(tester, h));
}

Future<void> _photographReviewAndConfirm(WidgetTester tester, AttendanceHarness h) async {
  Object? opened;
  Object? photo;
  Object? confirmed;
  h.server
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
  await h.openApp(tester);
  await h.openMeeting(tester);

  expect(opened, {'wedu_class_offering_id': 't-1', 'wedu_meeting_id': 'e-1'});
  expect(find.textContaining('3 aluno(s) com reconhecimento autorizado'), findsOneWidget);
  await tester.tap(find.text('Centro'));
  await tester.pumpAndSettle();
  final body = photo! as FormData;
  expect(body.fields.firstWhere((c) => c.key == 'angle').value, 'CENTER');
  expect(body.files.single.key, 'file');

  await tester.tap(find.text('Analisar 1 foto'));
  await tester.pumpAndSettle();
  expect(h.polls, 2, reason: 'espera o Persona processar a foto pendente');
  expect(h.camera.isOpen, isFalse);
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
}

Future<void> _notTheirClass(WidgetTester tester, AttendanceHarness h) async {
  h.server.on('POST sessions', (_) => (403, {'detail': 'professor não ministra esta turma no W-Edu'}));
  await h.openApp(tester);
  await h.openMeeting(tester);
  expect(find.text('Você não ministra esta turma.'), findsOneWidget);
}

Future<void> _confirmFailureKeepsReview(WidgetTester tester, AttendanceHarness h) async {
  h.server.on('POST sessions/s-1/confirm', (_) => (409, {'detail': 'present + absent precisa cobrir exatamente os matriculados ativos'}));
  await h.openApp(tester);
  await h.openMeeting(tester);
  await tester.tap(find.text('Centro'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Analisar 1 foto'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Confirmar chamada: 1 presente(s) de 4'));
  await tester.pumpAndSettle();
  expect(find.textContaining('matriculados ativos'), findsOneWidget);
  expect(find.text('Confirmar chamada: 1 presente(s) de 4'), findsOneWidget);
}

Future<void> _noPersonaNoAttendance(WidgetTester tester, AttendanceHarness h) async {
  await h.openApp(tester, persona: null);
  expect(find.text('Chamada facial'), findsNothing);
}

Future<void> _offlinePhotosSyncLater(WidgetTester tester, AttendanceHarness h) async {
  h.noInternet = true;
  final photos = <FormData>[];
  Object? confirmed;
  h.server
    ..on('POST sessions/s-1/images', (req) {
      if (h.noInternet) throw offline(req);
      photos.add(req.data as FormData);
      return (202, {'image_id': 'i', 'task_id': 'k'});
    })
    ..on('POST sessions/s-1/confirm', (req) {
      confirmed = req.data;
      return (200, {'session_id': 's-1', 'status': 'CONFIRMED', 'records_saved': 4});
    });
  await h.openApp(tester);
  await h.openMeeting(tester);

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
  expect(h.vault.files.keys.where((name) => name.startsWith('attendance_')), hasLength(2));
  expect(h.server.count('POST sessions/s-1/images'), 0);
  expect(h.camera.isOpen, isFalse);

  // A rede volta: ao abrir a chamada facial, o app envia sozinho e a chamada fica pronta para revisar.
  h.noInternet = false;
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
  expect(h.vault.files.keys.where((name) => name.startsWith('attendance_')), isEmpty, reason: 'confirmada, as fotos somem do aparelho');
}

Future<void> _offeringsFromCacheOffline(WidgetTester tester, AttendanceHarness h) async {
  await h.openApp(tester);
  await h.openMeeting(tester);

  // Outra abertura do app, agora sem rede: lista do cache.
  for (final route in [
    'GET users/me',
    'GET institutions/current',
    'GET access/me',
    'GET sync/versions',
    'GET assessment/teaching/offerings',
    'GET schedule/classes/t-1/meetings',
  ]) {
    h.server.on(route, (req) => throw offline(req));
  }
  await tester.pumpWidget(const SizedBox());
  await h.openApp(tester);
  await tester.tap(find.text('Chamada facial'));
  await tester.pumpAndSettle();
  expect(find.text('Matemática 6A'), findsOneWidget);
  await tester.tap(find.text('Matemática 6A'));
  await tester.pumpAndSettle();
  expect(find.text('Aula de hoje'), findsOneWidget);
}

Future<void> _signOutWarnsAndDeletesPhotos(WidgetTester tester, AttendanceHarness h) async {
  h.noInternet = true;
  await h.openApp(tester);
  await h.openMeeting(tester);
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
  expect(h.vault.files, isEmpty);
}
