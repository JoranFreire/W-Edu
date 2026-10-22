import 'dart:typed_data';

import 'package:dio/dio.dart';

import '../../../shared/face/challenge.dart';

/// Cadastro do próprio rosto no Persona: desafio de prova de vida e uma foto por passo.
class FaceEnrollmentRepository {
  FaceEnrollmentRepository(this._dio);

  final Dio _dio;

  Future<Challenge> challenge() async {
    final response = await _dio.post<Map<String, dynamic>>('liveness/challenge');
    return Challenge.fromJson(response.data!);
  }

  Future<void> enroll(String challengeId, List<Uint8List> photos) => _dio.post<void>(
    'me/enrollment',
    data: FormData.fromMap({
      'challenge_id': challengeId,
      'frames': [
        for (final (index, photo) in photos.indexed)
          MultipartFile.fromBytes(photo, filename: 'step$index.jpg', contentType: DioMediaType('image', 'jpeg')),
      ],
    }),
  );
}
