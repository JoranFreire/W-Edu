import 'package:dio/dio.dart';

/// Dependentes de quem está logado (JSON da API; `Dependent.list` lê).
class DependentsRepository {
  DependentsRepository(this._dio);

  final Dio _dio;

  Future<Object?> list() async => (await _dio.get<List<dynamic>>('guardians/me/dependents')).data;
}
