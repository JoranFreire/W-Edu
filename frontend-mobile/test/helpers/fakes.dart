import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/widgets.dart';
import 'package:wedu_mobile/core/cache/local_cache.dart';
import 'package:wedu_mobile/core/network/token_store.dart';
import 'package:wedu_mobile/features/auth/data/remembered_account.dart';
import 'package:wedu_mobile/shared/face/face_capture.dart';
import 'package:wedu_mobile/shared/vault/file_vault.dart';

/// Resposta programada: recebe a requisição e devolve (status, corpo JSON).
/// Lançar um [DioException] simula falha de rede.
typedef FakeRoute = (int, Object?) Function(RequestOptions req);

/// Servidor falso: cada requisição é casada por "MÉTODO caminho".
class FakeServer implements HttpClientAdapter {
  final Map<String, FakeRoute> routes = {};
  final List<RequestOptions> received = [];

  void on(String methodAndPath, FakeRoute route) => routes[methodAndPath] = route;

  int count(String methodAndPath) => received.where((r) => '${r.method} ${r.path}' == methodAndPath).length;

  @override
  Future<ResponseBody> fetch(RequestOptions options, Stream<Uint8List>? requestStream, Future<void>? cancelFuture) async {
    received.add(options);
    final key = '${options.method} ${options.path}';
    final route = routes[key];
    if (route == null) throw StateError('Rota não programada: $key');
    await Future<void>.delayed(Duration.zero);
    final (status, body) = route(options);
    return ResponseBody.fromString(
      jsonEncode(body),
      status,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType],
      },
    );
  }

  @override
  void close({bool force = false}) {}
}

DioException offline(RequestOptions req) => DioException.connectionError(requestOptions: req, reason: 'offline');

class InMemoryTokenStore implements TokenStore {
  InMemoryTokenStore([this.current]);

  String? current;

  @override
  Future<String?> read() async => current;

  @override
  Future<void> save(String token) async => current = token;

  @override
  Future<void> clear() async => current = null;
}

/// Cache em memória, com o mesmo contrato do arquivo (guarda o JSON, não o objeto).
class InMemoryCache implements LocalCache {
  final Map<String, String> entries = {};

  @override
  Future<CacheEntry?> read(String key) async {
    final text = entries[key];
    return text == null ? null : CacheEntry.fromJson(jsonDecode(text));
  }

  @override
  Future<void> save(String key, CacheEntry entry) async => entries[key] = jsonEncode(entry.toJson());

  @override
  Future<void> clear() async => entries.clear();
}

Map<String, dynamic> versionsJson({int notices = 1, int agenda = 1, int reportCard = 1, int dependents = 1}) => {
  'versions': {'notifications': notices, 'agenda': agenda, 'report_card': reportCard, 'dependents': dependents},
};

Map<String, dynamic> userJson({String role = 'student', List<String>? roles}) => {
  'id': 'u-1',
  'name': 'Ana Souza',
  'email': 'ana@escola.example.com',
  'role': role,
  'roles': roles ?? [role],
  'organization_id': null,
  'is_active': true,
  'created_at': '2026-02-01T10:00:00Z',
};

Map<String, dynamic> institutionJson() => {
  'id': 'i-1',
  'slug': 'escola-alfa',
  'name': 'Escola Alfa',
  'type': 'school',
  'branding': {'primary_color': '#059669', 'display_name': 'Colégio Alfa'},
};

Map<String, dynamic> noticeJson(String id, {bool read = false}) => {
  'id': id,
  'event_type': 'agenda_published',
  'title': 'Prova de Matemática',
  'body': 'Prova na sexta-feira.',
  'payload': {},
  'read_at': read ? '2026-10-01T12:00:00Z' : null,
  'created_at': '2026-10-01T10:00:00Z',
};

Map<String, dynamic> agendaJson(String id, {String day = '2099-10-03', String kind = 'test'}) => {
  'id': id,
  'class_group_id': 'g-1',
  'class_group_name': '6º ano A',
  'class_offering_id': null,
  'class_offering_name': 'Matemática',
  'kind': kind,
  'title': 'Prova bimestral',
  'description': 'Capítulos 1 a 3',
  'due_on': day,
  'created_at': '2026-10-01T10:00:00Z',
};

Map<String, dynamic> reportCardJson() => {
  'class_offering_id': 'o-1',
  'offering_name': 'Matemática',
  'periods': [
    {'name': '1º bimestre', 'average': 7.5, 'absences': 2},
  ],
  'final_grade': 7.5,
  'recovery_score': null,
  'attendance_rate': 0.92,
  'result': 'approved',
  'finalized': true,
  'passing_grade': 6.0,
  'min_attendance': 0.75,
};

Map<String, dynamic> dependentJson() => {
  'link_id': 'l-1',
  'student': {'id': 's-1', 'name': 'Bruno Souza', 'email': 'bruno@escola.example.com'},
  'relationship_kind': 'mother',
  'is_financial': true,
  'can_pick_up': true,
};

Map<String, dynamic> benefitJson(
  String id, {
  String status = 'released',
  String? validUntil,
  String item = 'Lanche',
  String kind = 'snack',
}) => {
  'id': id,
  'code': 'COD$id',
  'qr_payload': 'wedu-beneficio:COD$id',
  'status': status,
  'item_id': 'it-1',
  'item_name': item,
  'item_kind': kind,
  'unit': 'unidade',
  'quantity': 1,
  'student': {'id': 'u-1', 'name': 'Ana Souza', 'email': 'ana@escola.example.com'},
  'class_offering_id': 'o-1',
  'class_offering_name': 'Turma A',
  'scheduled_meeting_id': null,
  'valid_until': validUntil,
  'released_at': '2026-10-01T10:00:00Z',
  'redeemed_at': status == 'redeemed' ? '2026-10-01T12:00:00Z' : null,
};

Map<String, dynamic> accessJson({List<String> permissions = const []}) => {
  'role': 'student',
  'roles': ['student'],
  'permissions': permissions,
};

Map<String, dynamic> materialRequestJson(String id, {String status = 'approved', String? code}) => {
  'id': id,
  'requester': {'id': 'u-1', 'name': 'Ana Souza', 'email': 'ana@escola.example.com'},
  'class_offering_id': null,
  'class_offering_name': 'Artes 6A',
  'purpose': 'Mural da primavera',
  'needed_on': '2099-10-03',
  'status': status,
  'decision_note': null,
  'decided_at': null,
  'delivered_at': null,
  'return_due_on': null,
  'overdue': false,
  'created_at': '2026-10-01T10:00:00Z',
  'pickup_code': code,
  'qr_payload': code == null ? null : 'wedu-material:$code',
  'lines': [
    {
      'id': 'l-$id',
      'item_id': 'i-1',
      'item_name': 'Papel A4',
      'kind': 'consumable',
      'unit': 'resma',
      'quantity_requested': 3,
      'quantity_approved': 2,
      'quantity_delivered': 0,
      'quantity_returned': 0,
      'quantity_lost': 0,
      'outstanding': 0,
    },
  ],
};

class InMemoryRememberedAccountStore implements RememberedAccountStore {
  InMemoryRememberedAccountStore([this.current]);

  RememberedAccount? current;

  @override
  Future<RememberedAccount?> read() async => current;

  @override
  Future<void> save(RememberedAccount account) async => current = account;

  @override
  Future<void> forget() async => current = null;
}

const anasAccount = RememberedAccount(userId: 'u-1', institutionId: 'i-1', name: 'Ana Souza', email: 'ana@escola.example.com');

/// Câmera falsa: cada foto é um JPEG de mentira numerado.
class FakeCamera implements DeviceCameraCapture {
  FakeCamera({this.denied = false});

  final bool denied;
  int photos = 0;
  bool isOpen = false;

  @override
  Future<void> open() async {
    if (denied) throw StateError('sem permissão');
    isOpen = true;
  }

  @override
  Widget preview() => const SizedBox.expand();

  @override
  Future<Uint8List> takePhoto() async => Uint8List.fromList([0xFF, 0xD8, ++photos]);

  @override
  Future<void> close() async => isOpen = false;
}

/// Cofre em memória (o de verdade cifra em arquivo; ver test/shared/encrypted_vault_test.dart).
class InMemoryVault implements FileVault {
  final Map<String, Uint8List> files = {};

  @override
  Future<void> store(String name, Uint8List content) async => files[name] = content;

  @override
  Future<Uint8List?> read(String name) async => files[name];

  @override
  Future<void> delete(String name) async => files.remove(name);

  @override
  Future<void> deleteAll() async => files.clear();
}
