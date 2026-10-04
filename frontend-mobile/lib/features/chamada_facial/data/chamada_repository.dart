import 'dart:typed_data';

import 'package:dio/dio.dart';

import 'resultado_chamada.dart';

/// Chamada facial no Persona: abre a sessão do encontro, recebe as fotos da sala, devolve o
/// resultado para revisão e grava o que o professor confirmar (o Persona repassa ao W-Edu).
class ChamadaRepository {
  ChamadaRepository(this._dio);

  final Dio _dio;

  Future<SessaoChamada> abrir({required String turmaId, required String encontroId}) async {
    final resposta = await _dio.post<Map<String, dynamic>>(
      'sessions',
      data: {'wedu_class_offering_id': turmaId, 'wedu_meeting_id': encontroId},
    );
    return SessaoChamada.fromJson(resposta.data!);
  }

  Future<void> enviarFoto(String sessaoId, AnguloFoto angulo, Uint8List foto, DateTime tiradaEm) => _dio.post<void>(
        'sessions/$sessaoId/images',
        data: FormData.fromMap({
          'angle': angulo.valor,
          'captured_at': tiradaEm.toUtc().toIso8601String(),
          'file': MultipartFile.fromBytes(foto, filename: '${angulo.valor}.jpg', contentType: DioMediaType('image', 'jpeg')),
        }),
      );

  Future<ResultadoChamada> resultado(String sessaoId) async =>
      ResultadoChamada.fromJson((await _dio.get<Map<String, dynamic>>('sessions/$sessaoId/result')).data!);

  Future<int> confirmar(String sessaoId, {required Set<String> presentes, required Set<String> ausentes}) async {
    final resposta = await _dio.post<Map<String, dynamic>>(
      'sessions/$sessaoId/confirm',
      data: {'present': presentes.toList(), 'absent': ausentes.toList()},
    );
    return resposta.data!['records_saved'] as int? ?? 0;
  }

  /// Recorte do rosto ou foto do cadastro: o Persona manda o caminho absoluto (`/api/v1/...`).
  Future<Uint8List> imagem(String caminho) async {
    final resposta = await _dio.get<List<int>>(caminho, options: Options(responseType: ResponseType.bytes));
    return Uint8List.fromList(resposta.data!);
  }
}
