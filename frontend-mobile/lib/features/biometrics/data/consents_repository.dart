import 'package:dio/dio.dart';

import 'purpose.dart';
import 'biometric_status.dart';
import 'terms.dart';

/// Consentimentos no Persona: os da própria pessoa e, para o responsável, os do dependente menor.
class ConsentimentosRepository {
  ConsentimentosRepository(this._dio);

  final Dio _dio;

  Future<SituacaoBiometrica> minhaSituacao() => _situacao('consent/me/status');

  Future<SituacaoBiometrica> situacaoDoDependente(String alunoId) => _situacao('consent/dependents/$alunoId/status');

  Future<Termos> termos(Finalidade finalidade) async {
    final resposta = await _dio.get<Map<String, dynamic>>('consent/terms/${finalidade.valor}');
    return Termos.fromJson(resposta.data!);
  }

  Future<void> autorizar(Termos termos, {String? dependenteId}) => _dio.post<void>(
        dependenteId == null ? 'consent/grant' : 'consent/dependents/$dependenteId/grant',
        data: {'purpose': termos.finalidade.valor, 'terms_version': termos.versao, 'terms_hash': termos.hash},
      );

  Future<void> revogar(Finalidade finalidade, {String? dependenteId}) => _dio.post<void>(
        dependenteId == null ? 'consent/revoke' : 'consent/dependents/$dependenteId/revoke',
        data: {'purpose': finalidade.valor},
      );

  Future<SituacaoBiometrica> _situacao(String caminho) async {
    final resposta = await _dio.get<Map<String, dynamic>>(caminho);
    return SituacaoBiometrica.fromJson(resposta.data!);
  }
}
