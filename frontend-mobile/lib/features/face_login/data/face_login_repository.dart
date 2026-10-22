import 'dart:typed_data';

import 'package:dio/dio.dart';

import '../../../shared/face/challenge.dart';

/// API do Persona para o login facial: sorteia o desafio e confere as fotos.
/// As fotos vão só para o Persona e ficam em memória lá (nunca no W-Edu).
class FaceLoginRepository {
  FaceLoginRepository(this._dio);

  final Dio _dio;

  Future<Challenge> challenge(String userId) async {
    final response = await _dio.post<Map<String, dynamic>>('liveness/login-challenge', data: {'wedu_user_id': userId});
    return Challenge.fromJson(response.data!);
  }

  /// Uma foto por passo, na ordem do desafio. Devolve o assertion assinado.
  Future<String> verify({
    required String userId,
    required String institutionId,
    required String challengeId,
    required List<Uint8List> photos,
  }) async {
    final body = FormData.fromMap({
      'wedu_user_id': userId,
      'institution_id': institutionId,
      'challenge_id': challengeId,
      'frames': [
        for (final (index, photo) in photos.indexed)
          MultipartFile.fromBytes(photo, filename: 'step$index.jpg', contentType: DioMediaType('image', 'jpeg')),
      ],
    });
    final response = await _dio.post<Map<String, dynamic>>('auth/face/verify', data: body);
    return response.data!['assertion'] as String;
  }
}
