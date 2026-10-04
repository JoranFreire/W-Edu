import 'dart:typed_data';

import 'package:dio/dio.dart';

import '../../../shared/face/challenge.dart';

/// Cadastro do próprio rosto no Persona: desafio de prova de vida e uma foto por passo.
class CadastroFacialRepository {
  CadastroFacialRepository(this._dio);

  final Dio _dio;

  Future<Desafio> desafio() async {
    final resposta = await _dio.post<Map<String, dynamic>>('liveness/challenge');
    return Desafio.fromJson(resposta.data!);
  }

  Future<void> cadastrar(String desafioId, List<Uint8List> fotos) => _dio.post<void>(
        'me/enrollment',
        data: FormData.fromMap({
          'challenge_id': desafioId,
          'frames': [
            for (final (indice, foto) in fotos.indexed)
              MultipartFile.fromBytes(foto, filename: 'passo$indice.jpg', contentType: DioMediaType('image', 'jpeg')),
          ],
        }),
      );
}
