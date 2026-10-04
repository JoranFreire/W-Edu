import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import '../../shared/face/face.dart';
import 'data/biometric_status.dart';
import 'data/consents_repository.dart';
import 'data/face_enrollment_repository.dart';
import 'data/purpose.dart';
import 'data/terms.dart';

/// Nulos quando o Persona não está configurado (a tela nem aparece).
final consentsRepositoryProvider = Provider<ConsentsRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : ConsentsRepository(dio);
});

final faceEnrollmentRepositoryProvider = Provider<FaceEnrollmentRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : FaceEnrollmentRepository(dio);
});

/// Situação de quem está logado (sempre da rede: autorizar e revogar valem na hora).
final myBiometricStatusProvider = FutureProvider.autoDispose<BiometricStatus>((ref) => ref.watch(consentsRepositoryProvider)!.myStatus());

final dependentBiometricStatusProvider = FutureProvider.autoDispose.family<BiometricStatus, String>(
  (ref, studentId) => ref.watch(consentsRepositoryProvider)!.dependentStatus(studentId),
);

/// Autorizar (depois de ler o termo) e revogar, da própria pessoa ou do dependente menor.
final consentActionsProvider = Provider<ConsentActions>(ConsentActions.new);

class ConsentActions {
  ConsentActions(this._ref);

  final Ref _ref;

  ConsentsRepository get _repo => _ref.read(consentsRepositoryProvider)!;

  Future<ConsentTerms> terms(Purpose purpose) => _repo.terms(purpose);

  Future<void> grant(ConsentTerms terms, {String? dependentId}) async {
    await _repo.grant(terms, dependentId: dependentId);
    _refresh(dependentId);
  }

  Future<void> revoke(Purpose purpose, {String? dependentId}) async {
    await _repo.revoke(purpose, dependentId: dependentId);
    _refresh(dependentId);
  }

  void _refresh(String? dependentId) =>
      dependentId == null ? _ref.invalidate(myBiometricStatusProvider) : _ref.invalidate(dependentBiometricStatusProvider(dependentId));
}

/// Etapas do cadastro do rosto.
sealed class EnrollmentStep {
  const EnrollmentStep();
}

class EnrollmentReady extends EnrollmentStep {
  const EnrollmentReady();
}

class EnrollmentOpeningCamera extends EnrollmentStep {
  const EnrollmentOpeningCamera();
}

class EnrollmentCapturing extends EnrollmentStep {
  const EnrollmentCapturing(this.step, this.current, this.total);
  final ChallengeStep step;
  final int current;
  final int total;
}

class EnrollmentSending extends EnrollmentStep {
  const EnrollmentSending();
}

class EnrollmentDone extends EnrollmentStep {
  const EnrollmentDone();
}

/// Por que não cadastrou (a tela traduz): sem Persona, sem câmera, ou o erro da API.
enum EnrollmentFailure { unavailable, cameraUnavailable, rejected }

class EnrollmentFailed extends EnrollmentStep {
  const EnrollmentFailed(this.reason, [this.error]);
  final EnrollmentFailure reason;

  /// O erro da API, para a tela ler o código do Persona (`no_active_consent`...).
  final Object? error;
}

final faceEnrollmentProvider = NotifierProvider.autoDispose<FaceEnrollmentNotifier, EnrollmentStep>(FaceEnrollmentNotifier.new);

/// Cadastro do próprio rosto: desafio → uma foto por passo → Persona confere a prova de vida e
/// guarda o modelo do rosto (cifrado). As fotos ficam só em memória no aparelho.
class FaceEnrollmentNotifier extends Notifier<EnrollmentStep> {
  DeviceCameraCapture? _camera;

  @override
  EnrollmentStep build() {
    ref.onDispose(() => _camera?.close());
    return const EnrollmentReady();
  }

  DeviceCameraCapture? get camera => _camera;

  Future<void> start() async {
    if (state is EnrollmentOpeningCamera || state is EnrollmentCapturing || state is EnrollmentSending) return;
    final repo = ref.read(faceEnrollmentRepositoryProvider);
    if (repo == null) {
      state = const EnrollmentFailed(EnrollmentFailure.unavailable);
      return;
    }
    state = const EnrollmentOpeningCamera();
    final DeviceCameraCapture camera = _camera ?? ref.read(faceCameraProvider);
    _camera = camera;
    try {
      await camera.open();
    } on Object {
      state = const EnrollmentFailed(EnrollmentFailure.cameraUnavailable);
      return;
    }
    try {
      final challenge = await repo.challenge();
      final photos = await captureSteps(
        camera: camera,
        challenge: challenge,
        pause: ref.read(stepPauseProvider),
        onStep: (step, current, total) => state = EnrollmentCapturing(step, current, total),
        keepGoing: () => ref.mounted,
      );
      if (!ref.mounted || photos.length < challenge.steps.length) return;
      state = const EnrollmentSending();
      await repo.enroll(challenge.id, photos);
      if (!ref.mounted) return;
      ref.invalidate(myBiometricStatusProvider);
      state = const EnrollmentDone();
    } on Object catch (error) {
      if (ref.mounted) state = EnrollmentFailed(EnrollmentFailure.rejected, error);
    } finally {
      await camera.close();
    }
  }
}
