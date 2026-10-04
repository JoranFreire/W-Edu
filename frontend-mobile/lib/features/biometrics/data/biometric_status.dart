import 'purpose.dart';

/// O que está ativo para uma pessoa no Persona (nunca o rosto em si).
class BiometricStatus {
  const BiometricStatus({
    required this.name,
    required this.isAdult,
    required this.decidesAlone,
    required this.purposes,
    required this.faceEnrolled,
  });

  final String name;

  /// 18 anos ou mais: pode autorizar a presença em aula.
  final bool isAdult;

  /// 16 anos ou mais: autoriza sozinho login e catraca; abaixo disso, o responsável.
  final bool decidesAlone;
  final Set<Purpose> purposes;
  final bool faceEnrolled;

  bool consented(Purpose purpose) => purposes.contains(purpose);

  /// O cadastro do rosto exige alguma autorização ativa.
  bool get canEnrollFace => purposes.isNotEmpty;

  factory BiometricStatus.fromJson(Map<String, dynamic> json) => BiometricStatus(
    name: json['person_name'] as String? ?? '',
    isAdult: json['is_adult'] as bool? ?? false,
    // Persona sem o campo: vale a maioridade (regra anterior).
    decidesAlone: json['decides_alone'] as bool? ?? json['is_adult'] as bool? ?? false,
    purposes: {for (final value in json['active_purposes'] as List<dynamic>? ?? const []) ?Purpose.of(value as String)},
    faceEnrolled: json['enrollment_status'] == 'active',
  );
}
