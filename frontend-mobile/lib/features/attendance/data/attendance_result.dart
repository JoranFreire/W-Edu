/// Ângulo de cada foto da sala (o Persona funde os ângulos para decidir).
enum AnguloFoto {
  esquerda('LEFT', 'Lado esquerdo'),
  centro('CENTER', 'Centro'),
  direita('RIGHT', 'Lado direito');

  const AnguloFoto(this.valor, this.nome);
  final String valor;
  final String nome;
}

/// Sessão de chamada aberta no Persona para um encontro.
class SessaoChamada {
  const SessaoChamada({required this.id, required this.comAutorizacao, required this.semAutorizacao});

  final String id;
  final int comAutorizacao;
  final int semAutorizacao;

  factory SessaoChamada.fromJson(Map<String, dynamic> json) => SessaoChamada(
        id: json['session_id'] as String,
        comAutorizacao: json['students_with_consent'] as int? ?? 0,
        semAutorizacao: json['students_without_consent'] as int? ?? 0,
      );
}

/// Como o aluno saiu nas fotos. O professor sempre revisa antes de confirmar.
enum SituacaoNaFoto { presente, conferir, ausente, semAutorizacao }

class AlunoNaChamada {
  const AlunoNaChamada({required this.pessoaId, required this.nome, required this.situacao, this.recorte, this.fotoCadastro});

  final String pessoaId;
  final String nome;
  final SituacaoNaFoto situacao;

  /// Caminhos no Persona do rosto achado na foto e da foto do cadastro (só para conferir).
  final String? recorte;
  final String? fotoCadastro;
}

class ResultadoChamada {
  const ResultadoChamada({required this.alunos, required this.fotosPendentes, required this.rostosDetectados});

  final List<AlunoNaChamada> alunos;
  final int fotosPendentes;
  final int rostosDetectados;

  Iterable<AlunoNaChamada> de(SituacaoNaFoto situacao) => alunos.where((a) => a.situacao == situacao);

  factory ResultadoChamada.fromJson(Map<String, dynamic> json) {
    AlunoNaChamada aluno(Object? item, SituacaoNaFoto situacao) {
      final dados = item as Map<String, dynamic>;
      return AlunoNaChamada(
        pessoaId: dados['person_id'] as String,
        nome: dados['name'] as String,
        situacao: situacao,
        recorte: dados['crop_url'] as String?,
        fotoCadastro: dados['enrollment_photo_url'] as String?,
      );
    }

    List<AlunoNaChamada> grupo(String chave, SituacaoNaFoto situacao) =>
        [for (final item in json[chave] as List<dynamic>? ?? const []) aluno(item, situacao)];

    return ResultadoChamada(
      alunos: [
        ...grupo('present', SituacaoNaFoto.presente),
        ...grupo('uncertain', SituacaoNaFoto.conferir),
        ...grupo('absent', SituacaoNaFoto.ausente),
        ...grupo('without_consent', SituacaoNaFoto.semAutorizacao),
      ],
      fotosPendentes: json['images_pending'] as int? ?? 0,
      rostosDetectados: (json['metrics'] as Map<String, dynamic>?)?['faces_detected'] as int? ?? 0,
    );
  }
}
