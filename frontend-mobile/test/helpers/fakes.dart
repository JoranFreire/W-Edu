import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:wedu_mobile/core/network/token_store.dart';

/// Resposta programada: recebe a requisição e devolve (status, corpo JSON).
/// Lançar um [DioException] simula falha de rede.
typedef Rota = (int, Object?) Function(RequestOptions req);

/// Servidor falso: cada requisição é casada por "MÉTODO caminho".
class ServidorFalso implements HttpClientAdapter {
  final Map<String, Rota> rotas = {};
  final List<RequestOptions> recebidas = [];

  void on(String metodoECaminho, Rota rota) => rotas[metodoECaminho] = rota;

  int contar(String metodoECaminho) => recebidas.where((r) => '${r.method} ${r.path}' == metodoECaminho).length;

  @override
  Future<ResponseBody> fetch(RequestOptions options, Stream<Uint8List>? requestStream, Future<void>? cancelFuture) async {
    recebidas.add(options);
    final chave = '${options.method} ${options.path}';
    final rota = rotas[chave];
    if (rota == null) throw StateError('Rota não programada: $chave');
    await Future<void>.delayed(Duration.zero);
    final (status, corpo) = rota(options);
    return ResponseBody.fromString(jsonEncode(corpo), status, headers: {
      Headers.contentTypeHeader: [Headers.jsonContentType],
    });
  }

  @override
  void close({bool force = false}) {}
}

DioException semRede(RequestOptions req) => DioException.connectionError(requestOptions: req, reason: 'offline');

class TokenStoreEmMemoria implements TokenStore {
  TokenStoreEmMemoria([this.atual]);

  String? atual;

  @override
  Future<String?> ler() async => atual;

  @override
  Future<void> salvar(String token) async => atual = token;

  @override
  Future<void> limpar() async => atual = null;
}

Map<String, dynamic> usuarioJson({String role = 'student', List<String>? roles}) => {
      'id': 'u-1',
      'name': 'Ana Souza',
      'email': 'ana@escola.example.com',
      'role': role,
      'roles': roles ?? [role],
      'organization_id': null,
      'is_active': true,
      'created_at': '2026-02-01T10:00:00Z',
    };

Map<String, dynamic> instituicaoJson() => {
      'id': 'i-1',
      'slug': 'escola-alfa',
      'name': 'Escola Alfa',
      'type': 'school',
      'branding': {'primary_color': '#059669', 'display_name': 'Colégio Alfa'},
    };

Map<String, dynamic> avisoJson(String id, {bool lido = false}) => {
      'id': id,
      'event_type': 'agenda_published',
      'title': 'Prova de Matemática',
      'body': 'Prova na sexta-feira.',
      'payload': {},
      'read_at': lido ? '2026-10-01T12:00:00Z' : null,
      'created_at': '2026-10-01T10:00:00Z',
    };

Map<String, dynamic> agendaJson(String id, {String dia = '2099-10-03', String kind = 'test'}) => {
      'id': id,
      'class_group_id': 'g-1',
      'class_group_name': '6º ano A',
      'class_offering_id': null,
      'class_offering_name': 'Matemática',
      'kind': kind,
      'title': 'Prova bimestral',
      'description': 'Capítulos 1 a 3',
      'due_on': dia,
      'created_at': '2026-10-01T10:00:00Z',
    };

Map<String, dynamic> boletimJson() => {
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

Map<String, dynamic> dependenteJson() => {
      'link_id': 'l-1',
      'student': {'id': 's-1', 'name': 'Bruno Souza', 'email': 'bruno@escola.example.com'},
      'relationship_kind': 'mother',
      'is_financial': true,
      'can_pick_up': true,
    };
