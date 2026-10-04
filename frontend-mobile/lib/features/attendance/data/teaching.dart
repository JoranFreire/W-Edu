/// Turma que o professor ministra (W-Edu, `assessment/teaching/offerings`).
class TeachingOffering {
  const TeachingOffering({required this.id, required this.name});

  final String id;
  final String name;

  static List<TeachingOffering> list(Object? json) => [
    for (final item in json as List<dynamic>)
      TeachingOffering(id: (item as Map<String, dynamic>)['id'] as String, name: item['name'] as String),
  ];
}

/// Encontro (aula) da turma no W-Edu: a chamada facial é de um encontro.
class Meeting {
  const Meeting({required this.id, required this.title, required this.startsAt, required this.isClosed});

  final String id;
  final String title;
  final DateTime startsAt;
  final bool isClosed;

  /// Abertos, do mais próximo de hoje para trás e para a frente (hoje primeiro).
  static List<Meeting> open(Object? json) {
    final meetings = [
      for (final item in json as List<dynamic>)
        Meeting(
          id: (item as Map<String, dynamic>)['id'] as String,
          title: item['title'] as String,
          startsAt: DateTime.parse(item['starts_at'] as String).toLocal(),
          isClosed: item['is_closed'] as bool? ?? false,
        ),
    ].where((m) => !m.isClosed).toList();
    final now = DateTime.now();
    return meetings..sort((a, b) => a.startsAt.difference(now).abs().compareTo(b.startsAt.difference(now).abs()));
  }
}
