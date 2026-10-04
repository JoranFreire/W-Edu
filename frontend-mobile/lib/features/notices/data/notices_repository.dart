import 'package:dio/dio.dart';

/// Caixa de avisos de quem está logado (`/notifications/me`). As leituras
/// devolvem o JSON da API, que o cache guarda como veio.
class AvisosRepository {
  AvisosRepository(this._dio);

  final Dio _dio;

  Future<Object?> listar() async => (await _dio.get<List<dynamic>>('notifications/me')).data;

  Future<Object?> resumo() async => (await _dio.get<Map<String, dynamic>>('notifications/me/summary')).data;

  Future<void> marcarLido(String id) => _dio.post<void>('notifications/me/$id/read');

  Future<void> marcarTodos() => _dio.post<void>('notifications/me/read-all');
}
