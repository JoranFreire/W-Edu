import 'package:dio/dio.dart';

import 'dependente.dart';

class DependentesRepository {
  DependentesRepository(this._dio);

  final Dio _dio;

  Future<List<Dependente>> listar() async {
    final resposta = await _dio.get<List<dynamic>>('guardians/me/dependents');
    return resposta.data!.map((item) => Dependente.fromJson(item as Map<String, dynamic>)).toList();
  }
}
