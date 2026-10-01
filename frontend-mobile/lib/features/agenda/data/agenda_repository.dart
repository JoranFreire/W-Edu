import 'package:dio/dio.dart';

/// Agenda escolar: a do aluno logado ou a de um dependente (portal do responsável).
/// Devolve o JSON da API, que o cache guarda como veio; `ItemAgenda.lista` lê.
class AgendaRepository {
  AgendaRepository(this._dio);

  final Dio _dio;

  Future<Object?> minha() => _buscar('school/my/agenda');

  Future<Object?> doDependente(String alunoId) => _buscar('guardians/me/dependents/$alunoId/agenda');

  Future<Object?> _buscar(String caminho) async => (await _dio.get<List<dynamic>>(caminho)).data;
}
