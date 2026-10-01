import 'package:dio/dio.dart';

import 'aviso.dart';

/// Caixa de avisos de quem está logado (`/notifications/me`).
class AvisosRepository {
  AvisosRepository(this._dio);

  final Dio _dio;

  Future<List<Aviso>> listar() async {
    final resposta = await _dio.get<List<dynamic>>('notifications/me');
    return resposta.data!.map((item) => Aviso.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<int> naoLidos() async {
    final resposta = await _dio.get<Map<String, dynamic>>('notifications/me/summary');
    return resposta.data!['unread'] as int;
  }

  Future<void> marcarLido(String id) => _dio.post<void>('notifications/me/$id/read');

  Future<void> marcarTodos() => _dio.post<void>('notifications/me/read-all');
}
