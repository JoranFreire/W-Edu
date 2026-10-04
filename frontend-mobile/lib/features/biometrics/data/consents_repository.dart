import 'package:dio/dio.dart';

import 'biometric_status.dart';
import 'purpose.dart';
import 'terms.dart';

/// Consentimentos no Persona: os da própria pessoa e, para o responsável, os do dependente menor.
class ConsentsRepository {
  ConsentsRepository(this._dio);

  final Dio _dio;

  Future<BiometricStatus> myStatus() => _status('consent/me/status');

  Future<BiometricStatus> dependentStatus(String studentId) => _status('consent/dependents/$studentId/status');

  Future<ConsentTerms> terms(Purpose purpose) async {
    final response = await _dio.get<Map<String, dynamic>>('consent/terms/${purpose.value}');
    return ConsentTerms.fromJson(response.data!);
  }

  Future<void> grant(ConsentTerms terms, {String? dependentId}) => _dio.post<void>(
    dependentId == null ? 'consent/grant' : 'consent/dependents/$dependentId/grant',
    data: {'purpose': terms.purpose.value, 'terms_version': terms.version, 'terms_hash': terms.hash},
  );

  Future<void> revoke(Purpose purpose, {String? dependentId}) =>
      _dio.post<void>(dependentId == null ? 'consent/revoke' : 'consent/dependents/$dependentId/revoke', data: {'purpose': purpose.value});

  Future<BiometricStatus> _status(String path) async {
    final response = await _dio.get<Map<String, dynamic>>(path);
    return BiometricStatus.fromJson(response.data!);
  }
}
