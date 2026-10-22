import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_error.dart';
import '../../core/network/network_providers.dart';
import '../../shared/face/face.dart';
import '../auth/auth_providers.dart';
import 'data/face_login_repository.dart';

/// Nulo quando o Persona não está configurado (o app fica só com senha).
final faceLoginRepositoryProvider = Provider<FaceLoginRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : FaceLoginRepository(dio);
});

/// Por que o rosto não entrou (a tela traduz). Recusa nunca diz o motivo real: o Persona também não diz.
enum FaceLoginFailure { unavailable, cameraUnavailable, network, refused }

/// Etapas da tela de login facial.
sealed class FaceLoginStep {
  const FaceLoginStep();
}

class FaceLoginReady extends FaceLoginStep {
  const FaceLoginReady();
}

class FaceLoginOpeningCamera extends FaceLoginStep {
  const FaceLoginOpeningCamera();
}

class FaceLoginCapturing extends FaceLoginStep {
  const FaceLoginCapturing(this.step, this.current, this.total);
  final ChallengeStep step;
  final int current;
  final int total;
}

class FaceLoginChecking extends FaceLoginStep {
  const FaceLoginChecking();
}

/// O rosto não foi aceito (ou deu erro): a senha continua sempre disponível.
class FaceLoginFailed extends FaceLoginStep {
  const FaceLoginFailed(this.reason);
  final FaceLoginFailure reason;
}

final faceLoginProvider = NotifierProvider.autoDispose<FaceLoginNotifier, FaceLoginStep>(FaceLoginNotifier.new);

/// Prova de vida e login: desafio do Persona → uma foto por passo → Persona
/// confere e assina → o W-Edu troca o assertion pelo token. Qualquer recusa
/// leva à senha, sem dizer o motivo.
class FaceLoginNotifier extends Notifier<FaceLoginStep> {
  DeviceCameraCapture? _camera;

  @override
  FaceLoginStep build() {
    ref.onDispose(() => _camera?.close());
    return const FaceLoginReady();
  }

  /// O que a câmera vê (vazio antes de abrir).
  DeviceCameraCapture? get camera => _camera;

  Future<void> start() async {
    if (state is FaceLoginOpeningCamera || state is FaceLoginCapturing || state is FaceLoginChecking) return;
    final persona = ref.read(faceLoginRepositoryProvider);
    final account = await ref.read(rememberedAccountProvider.future);
    if (persona == null || account == null) {
      state = const FaceLoginFailed(FaceLoginFailure.unavailable);
      return;
    }

    state = const FaceLoginOpeningCamera();
    final DeviceCameraCapture camera = _camera ?? ref.read(faceCameraProvider);
    _camera = camera;
    try {
      await camera.open();
    } on Object {
      state = const FaceLoginFailed(FaceLoginFailure.cameraUnavailable);
      return;
    }

    try {
      final challenge = await persona.challenge(account.userId);
      final photos = await captureSteps(
        camera: camera,
        challenge: challenge,
        pause: ref.read(stepPauseProvider),
        onStep: (step, current, total) => state = FaceLoginCapturing(step, current, total),
        keepGoing: () => ref.mounted,
      );
      if (!ref.mounted || photos.length < challenge.steps.length) return;
      state = const FaceLoginChecking();
      final assertion = await persona.verify(
        userId: account.userId,
        institutionId: account.institutionId,
        challengeId: challenge.id,
        photos: photos,
      );
      // Deu certo: o router percebe a sessão e sai da tela sozinho.
      await ref.read(authProvider.notifier).signInWithFace(assertion);
    } on Object catch (error) {
      if (ref.mounted) state = FaceLoginFailed(isNetworkError(error) ? FaceLoginFailure.network : FaceLoginFailure.refused);
    } finally {
      await camera.close();
    }
  }
}
