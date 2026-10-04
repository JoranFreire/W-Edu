import '../../../core/theme/app_colors.dart';

/// Situação do aluno na disciplina, com as cores do site.
enum SubjectResult {
  inProgress('in_progress', BadgeColor.blue),
  recovery('recovery', BadgeColor.yellow),
  approved('approved', BadgeColor.green),
  failed('failed', BadgeColor.red),
  failedAttendance('failed_attendance', BadgeColor.red);

  const SubjectResult(this.value, this.color);
  final String value;
  final BadgeColor color;

  static SubjectResult of(String value) => values.firstWhere((result) => result.value == value, orElse: () => inProgress);
}

class ReportCardPeriod {
  const ReportCardPeriod({required this.name, required this.absences, this.average});

  final String name;
  final double? average;
  final int absences;

  factory ReportCardPeriod.fromJson(Map<String, dynamic> json) => ReportCardPeriod(
    name: json['name'] as String,
    average: (json['average'] as num?)?.toDouble(),
    absences: json['absences'] as int? ?? 0,
  );
}

/// Uma disciplina do boletim: médias das etapas fechadas e o resultado final, quando publicado.
class ReportCardSubject {
  const ReportCardSubject({
    required this.id,
    required this.name,
    required this.periods,
    required this.result,
    required this.finalized,
    required this.passingGrade,
    this.finalGrade,
    this.recoveryScore,
    this.attendanceRate,
  });

  final String id;
  final String name;
  final List<ReportCardPeriod> periods;
  final SubjectResult result;
  final bool finalized;
  final double passingGrade;
  final double? finalGrade;
  final double? recoveryScore;

  /// Fração de presença (0 a 1).
  final double? attendanceRate;

  static List<ReportCardSubject> list(Object? json) => [
    for (final item in json as List<dynamic>) ReportCardSubject.fromJson(item as Map<String, dynamic>),
  ];

  factory ReportCardSubject.fromJson(Map<String, dynamic> json) => ReportCardSubject(
    id: json['class_offering_id'] as String,
    name: json['offering_name'] as String,
    periods: (json['periods'] as List<dynamic>).map((e) => ReportCardPeriod.fromJson(e as Map<String, dynamic>)).toList(),
    result: SubjectResult.of(json['result'] as String),
    finalized: json['finalized'] as bool? ?? false,
    passingGrade: (json['passing_grade'] as num).toDouble(),
    finalGrade: (json['final_grade'] as num?)?.toDouble(),
    recoveryScore: (json['recovery_score'] as num?)?.toDouble(),
    attendanceRate: (json['attendance_rate'] as num?)?.toDouble(),
  );
}
