import 'attendance_result.dart';

/// Foto da sala tirada sem rede: os bytes ficam cifrados no cofre; aqui, só o que é preciso para enviar.
class PendingPhoto {
  const PendingPhoto({required this.angle, required this.takenAt, this.uploaded = false});

  final PhotoAngle angle;
  final DateTime takenAt;
  final bool uploaded;

  PendingPhoto markedUploaded() => PendingPhoto(angle: angle, takenAt: takenAt, uploaded: true);

  Map<String, Object?> toJson() => {'angle': angle.value, 'taken_at': takenAt.toUtc().toIso8601String(), 'uploaded': uploaded};

  factory PendingPhoto.fromJson(Map<String, dynamic> json) => PendingPhoto(
    angle: PhotoAngle.of(json['angle'] as String),
    takenAt: DateTime.parse(json['taken_at'] as String),
    uploaded: json['uploaded'] as bool? ?? false,
  );
}

/// Chamada fotografada sem rede, esperando o envio (e depois a revisão do professor).
class PendingAttendance {
  const PendingAttendance({
    required this.id,
    required this.offeringId,
    required this.meetingId,
    required this.title,
    required this.createdAt,
    this.photos = const [],
    this.sessionId,
  });

  final String id;
  final String offeringId;
  final String meetingId;

  /// Turma e encontro, para o professor reconhecer na lista.
  final String title;
  final DateTime createdAt;
  final List<PendingPhoto> photos;

  /// Sessão aberta no Persona no envio; com ela, a chamada só espera a revisão.
  final String? sessionId;

  bool get isUploaded => sessionId != null && photos.every((p) => p.uploaded);

  String photoName(PhotoAngle angle) => 'attendance_${id}_${angle.value}';

  PendingAttendance copyWith({List<PendingPhoto>? photos, String? sessionId}) => PendingAttendance(
    id: id,
    offeringId: offeringId,
    meetingId: meetingId,
    title: title,
    createdAt: createdAt,
    photos: photos ?? this.photos,
    sessionId: sessionId ?? this.sessionId,
  );

  Map<String, Object?> toJson() => {
    'id': id,
    'offering_id': offeringId,
    'meeting_id': meetingId,
    'title': title,
    'created_at': createdAt.toUtc().toIso8601String(),
    'session_id': sessionId,
    'photos': [for (final photo in photos) photo.toJson()],
  };

  factory PendingAttendance.fromJson(Map<String, dynamic> json) => PendingAttendance(
    id: json['id'] as String,
    offeringId: json['offering_id'] as String,
    meetingId: json['meeting_id'] as String,
    title: json['title'] as String,
    createdAt: DateTime.parse(json['created_at'] as String),
    sessionId: json['session_id'] as String?,
    photos: [for (final photo in json['photos'] as List<dynamic>) PendingPhoto.fromJson(photo as Map<String, dynamic>)],
  );
}
