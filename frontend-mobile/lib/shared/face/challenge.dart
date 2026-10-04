/// Passo da prova de vida, na ordem que o Persona sorteou. O servidor só exige
/// que os dois giros sejam para lados opostos (a câmera frontal pode espelhar),
/// então "esquerda" e "direita" são só para guiar a pessoa.
enum ChallengeStep {
  center('CENTER'),
  turnLeft('TURN_LEFT'),
  turnRight('TURN_RIGHT');

  const ChallengeStep(this.value);
  final String value;

  static ChallengeStep of(String value) => values.firstWhere((step) => step.value == value);
}

/// Desafio de prova de vida (uso único, vale cerca de 60 s).
class Challenge {
  const Challenge({required this.id, required this.steps});

  final String id;
  final List<ChallengeStep> steps;

  factory Challenge.fromJson(Map<String, dynamic> json) => Challenge(
    id: json['challenge_id'] as String,
    steps: [for (final step in json['steps'] as List<dynamic>) ChallengeStep.of(step as String)],
  );
}
