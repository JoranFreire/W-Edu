/// Endereço da API do Persona (reconhecimento facial), com o prefixo `api/v1/`.
///
/// Vem de `--dart-define=PERSONA_BASE_URL=...`. Vazio desliga o que depende do
/// rosto (o app segue só com senha). O app fala direto com o Persona: a imagem
/// do rosto nunca passa pelo backend do W-Edu (ADR 0012 do Persona).
class PersonaConfig {
  static const _definida = String.fromEnvironment('PERSONA_BASE_URL');

  static String? get baseUrl {
    if (_definida.isEmpty) return null;
    return _definida.endsWith('/') ? _definida : '$_definida/';
  }
}
