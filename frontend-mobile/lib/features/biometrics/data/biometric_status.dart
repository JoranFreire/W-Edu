import 'purpose.dart';

/// O que está ativo para uma pessoa no Persona (nunca o rosto em si).
class SituacaoBiometrica {
  const SituacaoBiometrica({
    required this.nome,
    required this.ehAdulto,
    required this.decideSozinho,
    required this.finalidades,
    required this.rostoCadastrado,
  });

  final String nome;

  /// 18 anos ou mais: pode autorizar a presença em aula.
  final bool ehAdulto;

  /// 16 anos ou mais: autoriza sozinho login e catraca; abaixo disso, o responsável.
  final bool decideSozinho;
  final Set<Finalidade> finalidades;
  final bool rostoCadastrado;

  bool autorizou(Finalidade finalidade) => finalidades.contains(finalidade);

  /// O cadastro do rosto exige alguma autorização ativa.
  bool get podeCadastrarRosto => finalidades.isNotEmpty;

  factory SituacaoBiometrica.fromJson(Map<String, dynamic> json) => SituacaoBiometrica(
        nome: json['person_name'] as String? ?? '',
        ehAdulto: json['is_adult'] as bool? ?? false,
        // Persona sem o campo: vale a maioridade (regra anterior).
        decideSozinho: json['decides_alone'] as bool? ?? json['is_adult'] as bool? ?? false,
        finalidades: {
          for (final valor in json['active_purposes'] as List<dynamic>? ?? const []) ?Finalidade.de(valor as String),
        },
        rostoCadastrado: json['enrollment_status'] == 'active',
      );
}
