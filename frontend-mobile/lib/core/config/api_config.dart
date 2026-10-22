import 'dart:io' show Platform;

/// Endereço da API do W-Edu (o backend FastAPI, direto, sem o proxy `/api` do site).
///
/// Vem de `--dart-define=API_BASE_URL=...` para que o mesmo build aponte para
/// homologação ou produção sem editar código. Sem ele, cai no backend local —
/// e no emulador Android "localhost" é o próprio emulador, não o Mac: o host
/// fica em 10.0.2.2.
class ApiConfig {
  static const _defined = String.fromEnvironment('API_BASE_URL');

  static String get baseUrl {
    if (_defined.isNotEmpty) return _defined.endsWith('/') ? _defined : '$_defined/';
    final host = Platform.isAndroid ? '10.0.2.2' : 'localhost';
    return 'http://$host:8000/';
  }

  static const connectTimeout = Duration(seconds: 15);
  static const receiveTimeout = Duration(seconds: 30);
}
