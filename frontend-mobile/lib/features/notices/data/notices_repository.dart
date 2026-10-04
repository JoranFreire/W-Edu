import 'package:dio/dio.dart';

/// Caixa de avisos de quem está logado (`/notifications/me`). As leituras
/// devolvem o JSON da API, que o cache guarda como veio.
class NoticesRepository {
  NoticesRepository(this._dio);

  final Dio _dio;

  Future<Object?> list() async => (await _dio.get<List<dynamic>>('notifications/me')).data;

  Future<Object?> summary() async => (await _dio.get<Map<String, dynamic>>('notifications/me/summary')).data;

  Future<void> markAsRead(String id) => _dio.post<void>('notifications/me/$id/read');

  Future<void> markAllAsRead() => _dio.post<void>('notifications/me/read-all');
}
