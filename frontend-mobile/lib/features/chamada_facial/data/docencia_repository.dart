import 'package:dio/dio.dart';

import 'docencia.dart';

/// Do W-Edu: turmas que o professor ministra e os encontros de cada uma.
class DocenciaRepository {
  DocenciaRepository(this._dio);

  final Dio _dio;

  Future<List<TurmaDocente>> turmas() async =>
      TurmaDocente.lista((await _dio.get<List<dynamic>>('assessment/teaching/offerings')).data);

  Future<List<Encontro>> encontros(String turmaId) async =>
      Encontro.abertos((await _dio.get<List<dynamic>>('schedule/classes/$turmaId/meetings')).data);
}
