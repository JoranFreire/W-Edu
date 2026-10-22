/// Um aviso da caixa de entrada (comunicado interno endereçado a quem está logado).
class Notice {
  const Notice({required this.id, required this.type, required this.title, required this.body, required this.createdAt, this.readAt});

  final String id;
  final String type;
  final String title;
  final String body;
  final DateTime createdAt;
  final DateTime? readAt;

  bool get isRead => readAt != null;

  Notice markedAsRead() => Notice(id: id, type: type, title: title, body: body, createdAt: createdAt, readAt: readAt ?? DateTime.now());

  static List<Notice> list(Object? json) => [for (final item in json as List<dynamic>) Notice.fromJson(item as Map<String, dynamic>)];

  /// Mesmo formato da API: é o que volta para o cache depois de marcar como lido.
  Map<String, Object?> toJson() => {
    'id': id,
    'event_type': type,
    'title': title,
    'body': body,
    'created_at': createdAt.toIso8601String(),
    'read_at': readAt?.toIso8601String(),
  };

  factory Notice.fromJson(Map<String, dynamic> json) => Notice(
    id: json['id'] as String,
    type: json['event_type'] as String,
    title: json['title'] as String,
    body: json['body'] as String? ?? '',
    createdAt: DateTime.parse(json['created_at'] as String),
    readAt: json['read_at'] == null ? null : DateTime.parse(json['read_at'] as String),
  );
}
