import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/widgets.dart';
import 'package:wedu_mobile/core/cache/cache_local.dart';
import 'package:wedu_mobile/features/auth/data/conta_lembrada.dart';
import 'package:wedu_mobile/shared/rosto/captura_de_rosto.dart';
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

/// Cache em memória, com o mesmo contrato do arquivo (guarda o JSON, não o objeto).
class CacheEmMemoria implements CacheLocal {
  final Map<String, String> entradas = {};

  @override
  Future<EntradaCache?> ler(String chave) async {
    final texto = entradas[chave];
    return texto == null ? null : EntradaCache.fromJson(jsonDecode(texto));
  }

  @override
  Future<void> salvar(String chave, EntradaCache entrada) async => entradas[chave] = jsonEncode(entrada.toJson());

  @override
  Future<void> limpar() async => entradas.clear();
}

Map<String, dynamic> versoesJson({int avisos = 1, int agenda = 1, int boletim = 1, int dependentes = 1}) => {
      'versions': {'notifications': avisos, 'agenda': agenda, 'report_card': boletim, 'dependents': dependentes},
    };

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

Map<String, dynamic> beneficioJson(String id, {String status = 'released', String? validoAte, String item = 'Lanche', String tipo = 'snack'}) => {
      'id': id,
      'code': 'COD$id',
      'qr_payload': 'wedu-beneficio:COD$id',
      'status': status,
      'item_id': 'it-1',
      'item_name': item,
      'item_kind': tipo,
      'unit': 'unidade',
      'quantity': 1,
      'student': {'id': 'u-1', 'name': 'Ana Souza', 'email': 'ana@escola.example.com'},
      'class_offering_id': 'o-1',
      'class_offering_name': 'Turma A',
      'scheduled_meeting_id': null,
      'valid_until': validoAte,
      'released_at': '2026-10-01T10:00:00Z',
      'redeemed_at': status == 'redeemed' ? '2026-10-01T12:00:00Z' : null,
    };

Map<String, dynamic> acessoJson({List<String> permissoes = const []}) => {'role': 'student', 'roles': ['student'], 'permissions': permissoes};

Map<String, dynamic> requisicaoJson(String id, {String status = 'approved', String? codigo}) => {
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
      'pickup_code': codigo,
      'qr_payload': codigo == null ? null : 'wedu-material:$codigo',
      'lines': [
        {'id': 'l-$id', 'item_id': 'i-1', 'item_name': 'Papel A4', 'kind': 'consumable', 'unit': 'resma', 'quantity_requested': 3,
         'quantity_approved': 2, 'quantity_delivered': 0, 'quantity_returned': 0, 'quantity_lost': 0, 'outstanding': 0},
      ],
    };

class ContaLembradaEmMemoria implements ContaLembradaStore {
  ContaLembradaEmMemoria([this.atual]);

  ContaLembrada? atual;

  @override
  Future<ContaLembrada?> ler() async => atual;

  @override
  Future<void> salvar(ContaLembrada conta) async => atual = conta;

  @override
  Future<void> esquecer() async => atual = null;
}

const contaDaAna = ContaLembrada(usuarioId: 'u-1', instituicaoId: 'i-1', nome: 'Ana Souza', email: 'ana@escola.example.com');

/// Câmera falsa: cada foto é um JPEG de mentira numerado.
class CameraFalsa implements CapturaDeRosto {
  CameraFalsa({this.semPermissao = false});

  final bool semPermissao;
  int fotos = 0;
  bool aberta = false;

  @override
  Future<void> abrir() async {
    if (semPermissao) throw StateError('sem permissão');
    aberta = true;
  }

  @override
  Widget visor() => const SizedBox.expand();

  @override
  Future<Uint8List> fotografar() async => Uint8List.fromList([0xFF, 0xD8, ++fotos]);

  @override
  Future<void> fechar() async => aberta = false;
}
