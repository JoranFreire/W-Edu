import 'package:dio/dio.dart';

/// Dependentes de quem está logado (JSON da API; `Dependente.lista` lê).
class DependentesRepository {
  DependentesRepository(this._dio);

  final Dio _dio;

  Future<Object?> listar() async => (await _dio.get<List<dynamic>>('guardians/me/dependents')).data;
}
