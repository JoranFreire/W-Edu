/// Aluno vinculado ao responsável logado.
class Dependent {
  const Dependent({
    required this.linkId,
    required this.studentId,
    required this.name,
    required this.relationship,
    required this.isFinancial,
  });

  final String linkId;
  final String studentId;
  final String name;

  /// Parentesco do responsável (`mother`, `father`, `legal_guardian`, `grandparent`, `other`).
  final String relationship;
  final bool isFinancial;

  String get firstName => name.split(' ').first;

  static List<Dependent> list(Object? json) => [for (final item in json as List<dynamic>) Dependent.fromJson(item as Map<String, dynamic>)];

  factory Dependent.fromJson(Map<String, dynamic> json) {
    final student = json['student'] as Map<String, dynamic>;
    return Dependent(
      linkId: json['link_id'] as String,
      studentId: student['id'] as String,
      name: student['name'] as String,
      relationship: json['relationship_kind'] as String,
      isFinancial: json['is_financial'] as bool? ?? false,
    );
  }
}
