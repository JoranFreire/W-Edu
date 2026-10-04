import 'dart:typed_data';

import 'package:dio/dio.dart';

import '../../../shared/face/challenge.dart';

/// API do Persona para o login facial: sorteia o desafio e confere as fotos.
/// As fotos vão só para o Persona e ficam em memória lá (nunca no W-Edu).
class PersonaRepository {
  PersonaRepository(this._dio);

  final Dio _dio;

  Future<Desafio> desafio(String usuarioId) async {
    final resposta = await _dio.post<Map<String, dynamic>>('liveness/login-challenge', data: {'wedu_user_id': usuarioId});
    return Desafio.fromJson(resposta.data!);
  }

  /// Uma foto por passo, na ordem do desafio. Devolve o assertion assinado.
  Future<String> verificar({
    required String usuarioId,
    required String instituicaoId,
    required String desafioId,
    required List<Uint8List> fotos,
  }) async {
    final corpo = FormData.fromMap({
      'wedu_user_id': usuarioId,
      'institution_id': instituicaoId,
      'challenge_id': desafioId,
      'frames': [
        for (final (indice, foto) in fotos.indexed) MultipartFile.fromBytes(foto, filename: 'passo$indice.jpg', contentType: DioMediaType('image', 'jpeg')),
      ],
    });
    final resposta = await _dio.post<Map<String, dynamic>>('auth/face/verify', data: corpo);
    return resposta.data!['assertion'] as String;
  }
}
