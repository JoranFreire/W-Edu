import 'purpose.dart';

/// Termo de consentimento vigente de uma finalidade: a autorização leva a versão e o hash,
/// e o Persona recusa (409) se o texto mudou desde que a pessoa o leu.
class ConsentTerms {
  const ConsentTerms({required this.purpose, required this.version, required this.text, required this.hash});

  final Purpose purpose;
  final String version;
  final String text;
  final String hash;

  factory ConsentTerms.fromJson(Map<String, dynamic> json) => ConsentTerms(
    purpose: Purpose.of(json['purpose'] as String)!,
    version: json['version'] as String,
    text: json['text'] as String,
    hash: json['hash'] as String,
  );
}
