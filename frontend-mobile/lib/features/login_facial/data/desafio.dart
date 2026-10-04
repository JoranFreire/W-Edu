/// Passo da prova de vida, na ordem que o Persona sorteou. O servidor só exige
/// que os dois giros sejam para lados opostos (a câmera frontal pode espelhar),
/// então "esquerda" e "direita" aqui são só para guiar a pessoa.
enum PassoDesafio {
  frente('CENTER', 'Olhe para a câmera'),
  esquerda('TURN_LEFT', 'Vire o rosto para a esquerda'),
  direita('TURN_RIGHT', 'Vire o rosto para a direita');

  const PassoDesafio(this.valor, this.instrucao);
  final String valor;
  final String instrucao;

  static PassoDesafio de(String valor) => values.firstWhere((p) => p.valor == valor);
}

/// Desafio de prova de vida (uso único, vale cerca de 60 s).
class Desafio {
  const Desafio({required this.id, required this.passos});

  final String id;
  final List<PassoDesafio> passos;

  factory Desafio.fromJson(Map<String, dynamic> json) => Desafio(
        id: json['challenge_id'] as String,
        passos: [for (final passo in json['steps'] as List<dynamic>) PassoDesafio.de(passo as String)],
      );
}
