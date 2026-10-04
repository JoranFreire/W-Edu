import 'resultado_chamada.dart';

/// Foto da sala tirada sem rede: os bytes ficam cifrados no cofre; aqui, só o que é preciso para enviar.
class FotoPendente {
  const FotoPendente({required this.angulo, required this.tiradaEm, this.enviada = false});

  final AnguloFoto angulo;
  final DateTime tiradaEm;
  final bool enviada;

  FotoPendente marcadaEnviada() => FotoPendente(angulo: angulo, tiradaEm: tiradaEm, enviada: true);

  Map<String, Object?> toJson() => {'angulo': angulo.valor, 'tirada_em': tiradaEm.toUtc().toIso8601String(), 'enviada': enviada};

  factory FotoPendente.fromJson(Map<String, dynamic> json) => FotoPendente(
        angulo: AnguloFoto.values.firstWhere((a) => a.valor == json['angulo']),
        tiradaEm: DateTime.parse(json['tirada_em'] as String),
        enviada: json['enviada'] as bool? ?? false,
      );
}

/// Chamada fotografada sem rede, esperando o envio (e depois a revisão do professor).
class ChamadaPendente {
  const ChamadaPendente({
    required this.id,
    required this.turmaId,
    required this.encontroId,
    required this.titulo,
    required this.criadaEm,
    this.fotos = const [],
    this.sessaoId,
  });

  final String id;
  final String turmaId;
  final String encontroId;

  /// Turma e encontro, para o professor reconhecer na lista.
  final String titulo;
  final DateTime criadaEm;
  final List<FotoPendente> fotos;

  /// Sessão aberta no Persona no envio; com ela, a chamada só espera a revisão.
  final String? sessaoId;

  bool get enviada => sessaoId != null && fotos.every((f) => f.enviada);

  String nomeDaFoto(AnguloFoto angulo) => 'chamada_${id}_${angulo.valor}';

  ChamadaPendente copiar({List<FotoPendente>? fotos, String? sessaoId}) => ChamadaPendente(
        id: id, turmaId: turmaId, encontroId: encontroId, titulo: titulo, criadaEm: criadaEm,
        fotos: fotos ?? this.fotos, sessaoId: sessaoId ?? this.sessaoId,
      );

  Map<String, Object?> toJson() => {
        'id': id, 'turma_id': turmaId, 'encontro_id': encontroId, 'titulo': titulo,
        'criada_em': criadaEm.toUtc().toIso8601String(), 'sessao_id': sessaoId,
        'fotos': [for (final foto in fotos) foto.toJson()],
      };

  factory ChamadaPendente.fromJson(Map<String, dynamic> json) => ChamadaPendente(
        id: json['id'] as String,
        turmaId: json['turma_id'] as String,
        encontroId: json['encontro_id'] as String,
        titulo: json['titulo'] as String,
        criadaEm: DateTime.parse(json['criada_em'] as String),
        sessaoId: json['sessao_id'] as String?,
        fotos: [for (final foto in json['fotos'] as List<dynamic>) FotoPendente.fromJson(foto as Map<String, dynamic>)],
      );
}
