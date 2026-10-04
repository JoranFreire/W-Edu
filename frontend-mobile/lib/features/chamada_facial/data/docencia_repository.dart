import 'package:dio/dio.dart';

/// Do W-Edu: turmas que o professor ministra e os encontros de cada uma. Devolve o JSON da API,
/// que o cache guarda (a chamada escolhe o encontro mesmo sem rede); `TurmaDocente.lista` e
/// `Encontro.abertos` leem.
class DocenciaRepository {
  DocenciaRepository(this._dio);

  final Dio _dio;

  Future<Object?> turmas() async => (await _dio.get<List<dynamic>>('assessment/teaching/offerings')).data;

  Future<Object?> encontros(String turmaId) async => (await _dio.get<List<dynamic>>('schedule/classes/$turmaId/meetings')).data;
}
