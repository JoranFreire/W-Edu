import 'dart:typed_data';

import 'challenge.dart';
import 'face_capture.dart';

/// Prova de vida no aparelho: para cada passo do desafio, avisa a tela, dá um
/// tempo para a pessoa se mexer e tira a foto. Quem confere é o Persona.
Future<List<Uint8List>> captureSteps({
  required DeviceCameraCapture camera,
  required Challenge challenge,
  required Duration pause,
  required void Function(ChallengeStep step, int current, int total) onStep,
  bool Function()? keepGoing,
}) async {
  final photos = <Uint8List>[];
  for (final (index, step) in challenge.steps.indexed) {
    if (keepGoing != null && !keepGoing()) break;
    onStep(step, index + 1, challenge.steps.length);
    await Future<void>.delayed(pause);
    photos.add(await camera.takePhoto());
  }
  return photos;
}
