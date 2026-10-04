import 'package:dio/dio.dart';

/// Benefícios liberados (QR de retirada) do aluno logado ou de um dependente.
/// Devolve o JSON da API, que o cache guarda como veio; `Beneficio.lista` lê.
class BeneficiosRepository {
  BeneficiosRepository(this._dio);

  final Dio _dio;

  Future<Object?> meus() => _buscar('social/my/vouchers');

  Future<Object?> doDependente(String alunoId) => _buscar('guardians/me/dependents/$alunoId/vouchers');

  Future<Object?> _buscar(String caminho) async => (await _dio.get<List<dynamic>>(caminho)).data;
}
