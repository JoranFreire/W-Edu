/// Um aviso da caixa de entrada (comunicado interno endereçado a quem está logado).
class Aviso {
  const Aviso({
    required this.id,
    required this.tipo,
    required this.titulo,
    required this.corpo,
    required this.criadoEm,
    this.lidoEm,
  });

  final String id;
  final String tipo;
  final String titulo;
  final String corpo;
  final DateTime criadoEm;
  final DateTime? lidoEm;

  bool get lido => lidoEm != null;

  Aviso marcadoComoLido() =>
      Aviso(id: id, tipo: tipo, titulo: titulo, corpo: corpo, criadoEm: criadoEm, lidoEm: lidoEm ?? DateTime.now());

  static List<Aviso> lista(Object? json) =>
      [for (final item in json as List<dynamic>) Aviso.fromJson(item as Map<String, dynamic>)];

  /// Mesmo formato da API: é o que volta para o cache depois de marcar como lido.
  Map<String, Object?> toJson() => {
        'id': id,
        'event_type': tipo,
        'title': titulo,
        'body': corpo,
        'created_at': criadoEm.toIso8601String(),
        'read_at': lidoEm?.toIso8601String(),
      };

  factory Aviso.fromJson(Map<String, dynamic> json) => Aviso(
        id: json['id'] as String,
        tipo: json['event_type'] as String,
        titulo: json['title'] as String,
        corpo: json['body'] as String? ?? '',
        criadoEm: DateTime.parse(json['created_at'] as String),
        lidoEm: json['read_at'] == null ? null : DateTime.parse(json['read_at'] as String),
      );
}
