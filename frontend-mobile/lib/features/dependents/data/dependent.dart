/// Aluno vinculado ao responsável logado.
class Dependente {
  const Dependente({
    required this.vinculoId,
    required this.alunoId,
    required this.nome,
    required this.parentesco,
    required this.responsavelFinanceiro,
  });

  final String vinculoId;
  final String alunoId;
  final String nome;
  final String parentesco;
  final bool responsavelFinanceiro;

  String get primeiroNome => nome.split(' ').first;

  static List<Dependente> lista(Object? json) =>
      [for (final item in json as List<dynamic>) Dependente.fromJson(item as Map<String, dynamic>)];

  factory Dependente.fromJson(Map<String, dynamic> json) {
    final aluno = json['student'] as Map<String, dynamic>;
    return Dependente(
      vinculoId: json['link_id'] as String,
      alunoId: aluno['id'] as String,
      nome: aluno['name'] as String,
      parentesco: json['relationship_kind'] as String,
      responsavelFinanceiro: json['is_financial'] as bool? ?? false,
    );
  }
}

/// Parentesco visto pelo responsável ("Você é: mãe").
const nomesDoParentesco = {
  'mother': 'Mãe',
  'father': 'Pai',
  'legal_guardian': 'Responsável legal',
  'grandparent': 'Avó/avô',
  'other': 'Responsável',
};
