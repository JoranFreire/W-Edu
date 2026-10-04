import 'package:dio/dio.dart';

/// Agenda escolar: a do aluno logado ou a de um dependente (portal do responsável).
/// Devolve o JSON da API, que o cache guarda como veio; `AgendaItem.list` lê.
class AgendaRepository {
  AgendaRepository(this._dio);

  final Dio _dio;

  Future<Object?> mine() => _fetch('school/my/agenda');

  Future<Object?> ofDependent(String studentId) => _fetch('guardians/me/dependents/$studentId/agenda');

  Future<Object?> _fetch(String path) async => (await _dio.get<List<dynamic>>(path)).data;
}
