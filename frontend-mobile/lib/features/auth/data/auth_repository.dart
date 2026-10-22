import 'package:dio/dio.dart';

import '../../../core/cache/local_cache.dart';
import '../../../core/network/token_store.dart';
import '../../../shared/vault/file_vault.dart';
import 'institution.dart';
import 'user.dart';

class AuthRepository {
  AuthRepository(this._dio, this._tokens, this._cache, this._vault);

  final Dio _dio;
  final TokenStore _tokens;
  final LocalCache _cache;
  final FileVault _vault;

  /// Pessoa e instituição da última conferência: o app abre com elas sem esperar a rede.
  static const _sessionKey = 'session';

  Future<bool> hasSession() async => await _tokens.read() != null;

  Future<User> signIn(String email, String password) async {
    final response = await _dio.post<Map<String, dynamic>>('auth/login', data: {'email': email.trim(), 'password': password});
    await _tokens.save(response.data!['access_token'] as String);
    return me();
  }

  /// Login facial: troca o assertion que o Persona emitiu (rosto conferido) pelo token.
  Future<User> signInWithFace(String assertion) async {
    final response = await _dio.post<Map<String, dynamic>>('auth/facial-login', data: {'assertion': assertion});
    await _tokens.save(response.data!['access_token'] as String);
    return me();
  }

  /// A pessoa, a instituição ativa (a do token) e as permissões nela, juntas. `Future.wait` repassa
  /// o próprio erro da API (o `.wait` de record o embrulharia e o 401 se perderia).
  Future<User> me() async {
    final [person, institution, access] = await Future.wait([
      _dio.get<Map<String, dynamic>>('users/me'),
      _dio.get<Map<String, dynamic>>('institutions/current'),
      _dio.get<Map<String, dynamic>>('access/me'),
    ]);
    final data = {'user': person.data!, 'institution': institution.data!, 'access': access.data!};
    final user = _parse(data);
    await _cache.save(_sessionKey, CacheEntry(null, data));
    return user;
  }

  Future<User?> savedSession() async {
    final saved = await _cache.read(_sessionKey);
    if (saved == null) return null;
    try {
      return _parse(saved.data);
    } on Object {
      return null;
    }
  }

  /// A API não guarda sessão no servidor: sair é esquecer o token e os dados
  /// pessoais guardados no aparelho (inclusive fotos de chamada ainda não enviadas).
  Future<void> signOut() async {
    await _tokens.clear();
    await _cache.clear();
    await _vault.deleteAll();
  }

  User _parse(Object? data) {
    final json = data as Map<String, dynamic>;
    final access = json['access'] as Map<String, dynamic>? ?? const {};
    return User.fromJson(
      json['user'] as Map<String, dynamic>,
      Institution.fromJson(json['institution'] as Map<String, dynamic>),
      permissions: (access['permissions'] as List<dynamic>? ?? const []).cast<String>(),
    );
  }
}
