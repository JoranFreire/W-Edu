import 'dart:typed_data';

import 'package:dio/dio.dart';

import 'attendance_result.dart';

/// Chamada facial no Persona: abre a sessão do encontro, recebe as fotos da sala, devolve o
/// resultado para revisão e grava o que o professor confirmar (o Persona repassa ao W-Edu).
class AttendanceRepository {
  AttendanceRepository(this._dio);

  final Dio _dio;

  Future<AttendanceSession> open({required String offeringId, required String meetingId}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      'sessions',
      data: {'wedu_class_offering_id': offeringId, 'wedu_meeting_id': meetingId},
    );
    return AttendanceSession.fromJson(response.data!);
  }

  Future<void> uploadPhoto(String sessionId, PhotoAngle angle, Uint8List photo, DateTime takenAt) => _dio.post<void>(
    'sessions/$sessionId/images',
    data: FormData.fromMap({
      'angle': angle.value,
      'captured_at': takenAt.toUtc().toIso8601String(),
      'file': MultipartFile.fromBytes(photo, filename: '${angle.value}.jpg', contentType: DioMediaType('image', 'jpeg')),
    }),
  );

  Future<AttendanceResult> result(String sessionId) async =>
      AttendanceResult.fromJson((await _dio.get<Map<String, dynamic>>('sessions/$sessionId/result')).data!);

  Future<int> confirm(String sessionId, {required Set<String> present, required Set<String> absent}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      'sessions/$sessionId/confirm',
      data: {'present': present.toList(), 'absent': absent.toList()},
    );
    return response.data!['records_saved'] as int? ?? 0;
  }

  /// Recorte do rosto ou foto do cadastro: o Persona manda o caminho absoluto (`/api/v1/...`).
  Future<Uint8List> image(String path) async {
    final response = await _dio.get<List<int>>(path, options: Options(responseType: ResponseType.bytes));
    return Uint8List.fromList(response.data!);
  }
}
