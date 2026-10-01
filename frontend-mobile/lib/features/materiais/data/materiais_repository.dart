import 'package:dio/dio.dart';

/// Requisições de material de quem está logado (JSON da API; `Requisicao.lista` lê).
class MateriaisRepository {
  MateriaisRepository(this._dio);

  final Dio _dio;

  Future<Object?> minhas() async => (await _dio.get<List<dynamic>>('warehouse/my/requests')).data;
}
