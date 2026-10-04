import 'package:dio/dio.dart';

/// Versão atual de cada área na instituição (`sync/versions`). Checagem leve:
/// o app só baixa de novo as telas cuja área mudou desde o cache.
class VersionsRepository {
  VersionsRepository(this._dio);

  final Dio _dio;

  Future<Map<String, int>> current() async {
    final response = await _dio.get<Map<String, dynamic>>('sync/versions');
    final versions = response.data!['versions'] as Map<String, dynamic>;
    return versions.map((area, version) => MapEntry(area, version as int));
  }
}
