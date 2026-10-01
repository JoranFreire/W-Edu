import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Onde o token de acesso mora entre uma abertura do app e outra.
///
/// A API do W-Edu emite só um token de acesso (sem refresh): ele já leva a
/// instituição ativa e vale até expirar; ao trocar de instituição, vem outro.
abstract interface class TokenStore {
  Future<String?> ler();
  Future<void> salvar(String token);
  Future<void> limpar();
}

/// Keychain no iOS, Keystore no Android. Guarda uma cópia em memória porque
/// ler o armazenamento seguro a cada requisição é lento.
class SecureTokenStore implements TokenStore {
  SecureTokenStore([FlutterSecureStorage? storage]) : _storage = storage ?? const FlutterSecureStorage();

  static const _chave = 'access_token';

  final FlutterSecureStorage _storage;
  String? _token;
  bool _carregado = false;

  @override
  Future<String?> ler() async {
    if (!_carregado) {
      _token = await _storage.read(key: _chave);
      _carregado = true;
    }
    return _token;
  }

  @override
  Future<void> salvar(String token) async {
    _token = token;
    _carregado = true;
    await _storage.write(key: _chave, value: token);
  }

  @override
  Future<void> limpar() async {
    _token = null;
    _carregado = true;
    await _storage.delete(key: _chave);
  }
}
