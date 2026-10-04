import 'package:dio/dio.dart';

/// Versão atual de cada área na instituição (`sync/versions`). Checagem leve:
/// o app só baixa de novo as telas cuja área mudou desde o cache.
class VersoesRepository {
  VersoesRepository(this._dio);

  final Dio _dio;

  Future<Map<String, int>> atuais() async {
    final resposta = await _dio.get<Map<String, dynamic>>('sync/versions');
    final versoes = resposta.data!['versions'] as Map<String, dynamic>;
    return versoes.map((area, versao) => MapEntry(area, versao as int));
  }
}
