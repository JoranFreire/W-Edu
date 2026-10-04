import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../data/biometric_status.dart';

/// Situação do cadastro do rosto e o atalho para cadastrar (ou refazer).
class FaceEnrollmentCard extends StatelessWidget {
  const FaceEnrollmentCard({super.key, required this.status});

  final BiometricStatus status;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final text = status.faceEnrolled
        ? l10n.faceEnrolled
        : status.canEnrollFace
        ? l10n.faceEnrollmentMissing
        : l10n.faceEnrollmentNeedsConsent;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(status.faceEnrolled ? Icons.verified_user_rounded : Icons.face_retouching_natural, color: theme.colorScheme.primary),
                const SizedBox(width: 12),
                Expanded(child: Text(text, style: theme.textTheme.bodyLarge)),
              ],
            ),
            const SizedBox(height: 12),
            FilledButton.tonal(
              onPressed: status.canEnrollFace ? () => context.go(Routes.faceEnrollment) : null,
              child: Text(status.faceEnrolled ? l10n.reenrollFace : l10n.enrollMyFace),
            ),
          ],
        ),
      ),
    );
  }
}
