import 'package:dio/dio.dart';

/// Do W-Edu: turmas que o professor ministra e os encontros de cada uma. Devolve o JSON da API,
/// que o cache guarda (a chamada escolhe o encontro mesmo sem rede); `TeachingOffering.list` e
/// `Meeting.open` leem.
class TeachingRepository {
  TeachingRepository(this._dio);

  final Dio _dio;

  Future<Object?> offerings() async => (await _dio.get<List<dynamic>>('assessment/teaching/offerings')).data;

  Future<Object?> meetings(String offeringId) async => (await _dio.get<List<dynamic>>('schedule/classes/$offeringId/meetings')).data;
}
