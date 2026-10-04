import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/face/face.dart';
import '../face_login_providers.dart';

/// O meio da tela: orientação, visor da câmera com o passo pedido, conferência ou recusa.
class FaceLoginStepView extends StatelessWidget {
  const FaceLoginStepView({super.key, required this.step, this.preview});

  final FaceLoginStep step;
  final Widget? preview;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return switch (step) {
      FaceLoginReady() => _Message(icon: Icons.face_rounded, text: l10n.faceLoginIntro),
      FaceLoginOpeningCamera() || FaceLoginChecking() => Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(step is FaceLoginChecking ? l10n.faceChecking : l10n.openingCamera, style: theme.textTheme.bodyLarge),
        ],
      ),
      FaceLoginCapturing(:final step, :final current, :final total) => StepViewfinder(
        step: step,
        current: current,
        total: total,
        preview: preview,
      ),
      FaceLoginFailed(:final reason) => _Message(
        icon: Icons.no_accounts_rounded,
        text: reason.message(l10n),
        color: theme.colorScheme.error,
      ),
    };
  }
}

extension FaceLoginFailureText on FaceLoginFailure {
  String message(AppLocalizations l10n) => switch (this) {
    FaceLoginFailure.unavailable => l10n.faceLoginUnavailable,
    FaceLoginFailure.cameraUnavailable => l10n.faceLoginCameraUnavailable,
    FaceLoginFailure.network => l10n.errorNoConnection,
    FaceLoginFailure.refused => l10n.faceLoginRefused,
  };
}

class _Message extends StatelessWidget {
  const _Message({required this.icon, required this.text, this.color});

  final IconData icon;
  final String text;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 72, color: color ?? theme.colorScheme.primary),
        const SizedBox(height: 16),
        Text(
          text,
          textAlign: TextAlign.center,
          style: theme.textTheme.bodyLarge?.copyWith(color: color),
        ),
      ],
    );
  }
}
