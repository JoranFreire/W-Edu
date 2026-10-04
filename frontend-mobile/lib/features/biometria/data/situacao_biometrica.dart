import 'finalidade.dart';

/// O que está ativo para uma pessoa no Persona (nunca o rosto em si).
class SituacaoBiometrica {
  const SituacaoBiometrica({required this.nome, required this.ehAdulto, required this.finalidades, required this.rostoCadastrado});

  final String nome;
  final bool ehAdulto;
  final Set<Finalidade> finalidades;
  final bool rostoCadastrado;

  bool autorizou(Finalidade finalidade) => finalidades.contains(finalidade);

  /// O cadastro do rosto exige alguma autorização ativa.
  bool get podeCadastrarRosto => finalidades.isNotEmpty;

  factory SituacaoBiometrica.fromJson(Map<String, dynamic> json) => SituacaoBiometrica(
        nome: json['person_name'] as String? ?? '',
        ehAdulto: json['is_adult'] as bool? ?? false,
        finalidades: {
          for (final valor in json['active_purposes'] as List<dynamic>? ?? const []) ?Finalidade.de(valor as String),
        },
        rostoCadastrado: json['enrollment_status'] == 'active',
      );
}
