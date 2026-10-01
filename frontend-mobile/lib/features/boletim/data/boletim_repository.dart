import 'package:dio/dio.dart';

import 'boletim.dart';

/// Boletim do aluno logado ou de um dependente (portal do responsável).
class BoletimRepository {
  BoletimRepository(this._dio);

  final Dio _dio;

  Future<List<DisciplinaBoletim>> meu() => _listar('assessment/my/report-card');

  Future<List<DisciplinaBoletim>> doDependente(String alunoId) => _listar('guardians/me/dependents/$alunoId/report-card');

  Future<List<DisciplinaBoletim>> _listar(String caminho) async {
    final resposta = await _dio.get<List<dynamic>>(caminho);
    return resposta.data!.map((item) => DisciplinaBoletim.fromJson(item as Map<String, dynamic>)).toList();
  }
}
