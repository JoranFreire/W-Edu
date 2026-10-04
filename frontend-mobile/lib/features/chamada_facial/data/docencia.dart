/// Turma que o professor ministra (W-Edu, `assessment/teaching/offerings`).
class TurmaDocente {
  const TurmaDocente({required this.id, required this.nome});

  final String id;
  final String nome;

  static List<TurmaDocente> lista(Object? json) => [
        for (final item in json as List<dynamic>)
          TurmaDocente(id: (item as Map<String, dynamic>)['id'] as String, nome: item['name'] as String),
      ];
}

/// Encontro (aula) da turma no W-Edu: a chamada facial é de um encontro.
class Encontro {
  const Encontro({required this.id, required this.titulo, required this.inicio, required this.encerrado});

  final String id;
  final String titulo;
  final DateTime inicio;
  final bool encerrado;

  /// Abertos, do mais próximo de hoje para trás e para a frente (hoje primeiro).
  static List<Encontro> abertos(Object? json) {
    final encontros = [
      for (final item in json as List<dynamic>)
        Encontro(
          id: (item as Map<String, dynamic>)['id'] as String,
          titulo: item['title'] as String,
          inicio: DateTime.parse(item['starts_at'] as String).toLocal(),
          encerrado: item['is_closed'] as bool? ?? false,
        ),
    ].where((e) => !e.encerrado).toList();
    final agora = DateTime.now();
    return encontros..sort((a, b) => a.inicio.difference(agora).abs().compareTo(b.inicio.difference(agora).abs()));
  }
}
