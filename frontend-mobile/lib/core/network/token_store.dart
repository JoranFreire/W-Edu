import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Onde o token de acesso mora entre uma abertura do app e outra.
///
/// A API do W-Edu emite só um token de acesso (sem refresh): ele já leva a
/// instituição ativa e vale até expirar; ao trocar de instituição, vem outro.
abstract interface class TokenStore {
  Future<String?> read();
  Future<void> save(String token);
  Future<void> clear();
}

/// Keychain no iOS, Keystore no Android. Guarda uma cópia em memória porque
/// ler o armazenamento seguro a cada requisição é lento.
class SecureTokenStore implements TokenStore {
  SecureTokenStore([FlutterSecureStorage? storage]) : _storage = storage ?? const FlutterSecureStorage();

  static const _key = 'access_token';

  final FlutterSecureStorage _storage;
  String? _token;
  bool _loaded = false;

  @override
  Future<String?> read() async {
    if (!_loaded) {
      _token = await _storage.read(key: _key);
      _loaded = true;
    }
    return _token;
  }

  @override
  Future<void> save(String token) async {
    _token = token;
    _loaded = true;
    await _storage.write(key: _key, value: token);
  }

  @override
  Future<void> clear() async {
    _token = null;
    _loaded = true;
    await _storage.delete(key: _key);
  }
}
