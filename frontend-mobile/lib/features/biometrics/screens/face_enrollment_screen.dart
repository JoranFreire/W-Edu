import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../../../shared/face/face.dart';
import '../biometrics_providers.dart';
import '../widgets/biometrics_labels.dart';

/// Cadastro do próprio rosto: a mesma prova de vida do login (de frente e virando para os dois lados).
class FaceEnrollmentScreen extends ConsumerWidget {
  const FaceEnrollmentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final step = ref.watch(faceEnrollmentProvider);
    final notifier = ref.read(faceEnrollmentProvider.notifier);
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.enrollmentTitle)),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: switch (step) {
                  EnrollmentReady() => _Notice(Icons.face_rounded, l10n.enrollmentIntro),
                  EnrollmentOpeningCamera() || EnrollmentSending() => const LoadingView(),
                  EnrollmentCapturing(:final step, :final current, :final total) => StepViewfinder(
                    step: step,
                    current: current,
                    total: total,
                    preview: notifier.camera?.preview(),
                  ),
                  EnrollmentDone() => _Notice(Icons.verified_user_rounded, l10n.enrollmentDone),
                  EnrollmentFailed() => _Notice(Icons.error_outline_rounded, _failureMessage(step, l10n), color: theme.colorScheme.error),
                },
              ),
              const SizedBox(height: 16),
              if (step is EnrollmentReady || step is EnrollmentFailed)
                FilledButton(onPressed: notifier.start, child: Text(step is EnrollmentFailed ? l10n.tryAgain : l10n.start)),
              if (step is EnrollmentDone) FilledButton(onPressed: () => context.go(Routes.biometrics), child: Text(l10n.finish)),
            ],
          ),
        ),
      ),
    );
  }

  String _failureMessage(EnrollmentFailed failed, AppLocalizations l10n) => switch (failed.reason) {
    EnrollmentFailure.unavailable => l10n.enrollmentUnavailable,
    EnrollmentFailure.cameraUnavailable => l10n.enrollmentCameraUnavailable,
    EnrollmentFailure.rejected => personaErrorMessage(failed.error!, l10n, fallback: l10n.enrollmentError),
  };
}

class _Notice extends StatelessWidget {
  const _Notice(this.icon, this.text, {this.color});

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
