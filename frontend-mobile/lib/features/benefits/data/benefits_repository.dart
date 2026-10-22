import 'package:dio/dio.dart';

/// Benefícios liberados (QR de retirada) do aluno logado ou de um dependente.
/// Devolve o JSON da API, que o cache guarda como veio; `Benefit.list` lê.
class BenefitsRepository {
  BenefitsRepository(this._dio);

  final Dio _dio;

  Future<Object?> mine() => _fetch('social/my/vouchers');

  Future<Object?> ofDependent(String studentId) => _fetch('guardians/me/dependents/$studentId/vouchers');

  Future<Object?> _fetch(String path) async => (await _dio.get<List<dynamic>>(path)).data;
}
