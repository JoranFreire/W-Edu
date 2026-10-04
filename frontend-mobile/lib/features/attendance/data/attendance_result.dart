/// Ângulo de cada foto da sala (o Persona funde os ângulos para decidir).
enum PhotoAngle {
  left('LEFT'),
  center('CENTER'),
  right('RIGHT');

  const PhotoAngle(this.value);
  final String value;

  static PhotoAngle of(String value) => values.firstWhere((a) => a.value == value);
}

/// Sessão de chamada aberta no Persona para um encontro.
class AttendanceSession {
  const AttendanceSession({required this.id, required this.withConsent, required this.withoutConsent});

  final String id;
  final int withConsent;
  final int withoutConsent;

  factory AttendanceSession.fromJson(Map<String, dynamic> json) => AttendanceSession(
    id: json['session_id'] as String,
    withConsent: json['students_with_consent'] as int? ?? 0,
    withoutConsent: json['students_without_consent'] as int? ?? 0,
  );
}

/// Como o aluno saiu nas fotos. O professor sempre revisa antes de confirmar.
enum PhotoOutcome { present, uncertain, absent, withoutConsent }

class AttendanceStudent {
  const AttendanceStudent({required this.personId, required this.name, required this.outcome, this.cropUrl, this.enrollmentPhotoUrl});

  final String personId;
  final String name;
  final PhotoOutcome outcome;

  /// Caminhos no Persona do rosto achado na foto e da foto do cadastro (só para conferir).
  final String? cropUrl;
  final String? enrollmentPhotoUrl;
}

class AttendanceResult {
  const AttendanceResult({required this.students, required this.pendingImages, required this.facesDetected});

  final List<AttendanceStudent> students;
  final int pendingImages;
  final int facesDetected;

  Iterable<AttendanceStudent> withOutcome(PhotoOutcome outcome) => students.where((s) => s.outcome == outcome);

  factory AttendanceResult.fromJson(Map<String, dynamic> json) {
    AttendanceStudent student(Object? item, PhotoOutcome outcome) {
      final data = item as Map<String, dynamic>;
      return AttendanceStudent(
        personId: data['person_id'] as String,
        name: data['name'] as String,
        outcome: outcome,
        cropUrl: data['crop_url'] as String?,
        enrollmentPhotoUrl: data['enrollment_photo_url'] as String?,
      );
    }

    List<AttendanceStudent> group(String key, PhotoOutcome outcome) => [
      for (final item in json[key] as List<dynamic>? ?? const []) student(item, outcome),
    ];

    return AttendanceResult(
      students: [
        ...group('present', PhotoOutcome.present),
        ...group('uncertain', PhotoOutcome.uncertain),
        ...group('absent', PhotoOutcome.absent),
        ...group('without_consent', PhotoOutcome.withoutConsent),
      ],
      pendingImages: json['images_pending'] as int? ?? 0,
      facesDetected: (json['metrics'] as Map<String, dynamic>?)?['faces_detected'] as int? ?? 0,
    );
  }
}
