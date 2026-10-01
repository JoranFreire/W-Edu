import '../../../core/theme/app_colors.dart';

/// Situação do aluno na disciplina, com os nomes e as cores do site.
enum ResultadoDisciplina {
  cursando('in_progress', 'Cursando', BadgeCor.azul),
  recuperacao('recovery', 'Em recuperação', BadgeCor.amarelo),
  aprovado('approved', 'Aprovado', BadgeCor.verde),
  reprovado('failed', 'Reprovado', BadgeCor.vermelho),
  reprovadoPorFalta('failed_attendance', 'Reprovado por falta', BadgeCor.vermelho);

  const ResultadoDisciplina(this.valor, this.nome, this.cor);
  final String valor;
  final String nome;
  final BadgeCor cor;

  static ResultadoDisciplina de(String valor) =>
      values.firstWhere((resultado) => resultado.valor == valor, orElse: () => cursando);
}

class EtapaBoletim {
  const EtapaBoletim({required this.nome, required this.faltas, this.media});

  final String nome;
  final double? media;
  final int faltas;

  factory EtapaBoletim.fromJson(Map<String, dynamic> json) => EtapaBoletim(
        nome: json['name'] as String,
        media: (json['average'] as num?)?.toDouble(),
        faltas: json['absences'] as int? ?? 0,
      );
}

/// Uma disciplina do boletim: médias das etapas fechadas e o resultado final, quando publicado.
class DisciplinaBoletim {
  const DisciplinaBoletim({
    required this.id,
    required this.nome,
    required this.etapas,
    required this.resultado,
    required this.finalizada,
    required this.mediaAprovacao,
    this.notaFinal,
    this.recuperacao,
    this.frequencia,
  });

  final String id;
  final String nome;
  final List<EtapaBoletim> etapas;
  final ResultadoDisciplina resultado;
  final bool finalizada;
  final double mediaAprovacao;
  final double? notaFinal;
  final double? recuperacao;

  /// Fração de presença (0 a 1).
  final double? frequencia;

  factory DisciplinaBoletim.fromJson(Map<String, dynamic> json) => DisciplinaBoletim(
        id: json['class_offering_id'] as String,
        nome: json['offering_name'] as String,
        etapas: (json['periods'] as List<dynamic>).map((e) => EtapaBoletim.fromJson(e as Map<String, dynamic>)).toList(),
        resultado: ResultadoDisciplina.de(json['result'] as String),
        finalizada: json['finalized'] as bool? ?? false,
        mediaAprovacao: (json['passing_grade'] as num).toDouble(),
        notaFinal: (json['final_grade'] as num?)?.toDouble(),
        recuperacao: (json['recovery_score'] as num?)?.toDouble(),
        frequencia: (json['attendance_rate'] as num?)?.toDouble(),
      );
}
