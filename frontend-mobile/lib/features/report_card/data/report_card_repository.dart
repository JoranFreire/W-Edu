import 'package:dio/dio.dart';

/// Boletim do aluno logado ou de um dependente (portal do responsável).
/// Devolve o JSON da API, que o cache guarda como veio; `DisciplinaBoletim.lista` lê.
class BoletimRepository {
  BoletimRepository(this._dio);

  final Dio _dio;

  Future<Object?> meu() => _buscar('assessment/my/report-card');

  Future<Object?> doDependente(String alunoId) => _buscar('guardians/me/dependents/$alunoId/report-card');

  Future<Object?> _buscar(String caminho) async => (await _dio.get<List<dynamic>>(caminho)).data;
}
