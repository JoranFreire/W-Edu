import '../../../core/format/dates.dart';
import '../../../core/theme/app_colors.dart';

/// Tipos de item da agenda da turma, com as cores do site.
enum AgendaItemKind {
  homework('homework', BadgeColor.blue),
  test('test', BadgeColor.red),
  event('event', BadgeColor.purple),
  notice('notice', BadgeColor.yellow);

  const AgendaItemKind(this.value, this.color);
  final String value;
  final BadgeColor color;

  static AgendaItemKind of(String value) => values.firstWhere((kind) => kind.value == value, orElse: () => notice);
}

/// Tarefa, prova, evento ou aviso publicado na agenda da turma.
class AgendaItem {
  const AgendaItem({
    required this.id,
    required this.kind,
    required this.title,
    required this.date,
    required this.classGroup,
    this.description,
    this.subject,
  });

  final String id;
  final AgendaItemKind kind;
  final String title;
  final DateTime date;
  final String classGroup;
  final String? description;
  final String? subject;

  /// Lista da API (ou do cache), em ordem de data.
  static List<AgendaItem> list(Object? json) =>
      [for (final item in json as List<dynamic>) AgendaItem.fromJson(item as Map<String, dynamic>)]
        ..sort((a, b) => a.date.compareTo(b.date));

  factory AgendaItem.fromJson(Map<String, dynamic> json) => AgendaItem(
    id: json['id'] as String,
    kind: AgendaItemKind.of(json['kind'] as String),
    title: json['title'] as String,
    date: parseDay(json['due_on'] as String),
    classGroup: json['class_group_name'] as String,
    description: json['description'] as String?,
    subject: json['class_offering_name'] as String?,
  );
}
