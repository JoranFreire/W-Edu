import 'package:dio/dio.dart';

/// Boletim do aluno logado ou de um dependente (portal do responsável).
/// Devolve o JSON da API, que o cache guarda como veio; `ReportCardSubject.list` lê.
class ReportCardRepository {
  ReportCardRepository(this._dio);

  final Dio _dio;

  Future<Object?> mine() => _fetch('assessment/my/report-card');

  Future<Object?> ofDependent(String studentId) => _fetch('guardians/me/dependents/$studentId/report-card');

  Future<Object?> _fetch(String path) async => (await _dio.get<List<dynamic>>(path)).data;
}
