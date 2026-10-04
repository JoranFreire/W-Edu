import 'finalidade.dart';

/// Termo de consentimento vigente de uma finalidade: a autorização leva a versão e o hash,
/// e o Persona recusa (409) se o texto mudou desde que a pessoa o leu.
class Termos {
  const Termos({required this.finalidade, required this.versao, required this.texto, required this.hash});

  final Finalidade finalidade;
  final String versao;
  final String texto;
  final String hash;

  factory Termos.fromJson(Map<String, dynamic> json) => Termos(
        finalidade: Finalidade.de(json['purpose'] as String)!,
        versao: json['version'] as String,
        texto: json['text'] as String,
        hash: json['hash'] as String,
      );
}
