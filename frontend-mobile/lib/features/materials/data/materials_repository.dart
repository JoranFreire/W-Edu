import 'package:dio/dio.dart';

/// Requisições de material de quem está logado (JSON da API; `MaterialRequest.list` lê).
class MaterialsRepository {
  MaterialsRepository(this._dio);

  final Dio _dio;

  Future<Object?> mine() async => (await _dio.get<List<dynamic>>('warehouse/my/requests')).data;
}
