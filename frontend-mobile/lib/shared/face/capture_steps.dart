import 'dart:typed_data';

import 'face_capture.dart';
import 'challenge.dart';

/// Prova de vida no aparelho: para cada passo do desafio, avisa a tela, dá um
/// tempo para a pessoa se mexer e tira a foto. Quem confere é o Persona.
Future<List<Uint8List>> capturarPassos({
  required CapturaDeRosto captura,
  required Desafio desafio,
  required Duration pausa,
  required void Function(PassoDesafio passo, int numero, int total) aoMudarDePasso,
  bool Function()? continuar,
}) async {
  final fotos = <Uint8List>[];
  for (final (indice, passo) in desafio.passos.indexed) {
    if (continuar != null && !continuar()) break;
    aoMudarDePasso(passo, indice + 1, desafio.passos.length);
    await Future<void>.delayed(pausa);
    fotos.add(await captura.fotografar());
  }
  return fotos;
}
