import 'package:flutter/material.dart';

import '../../l10n/l10n.dart';
import 'challenge.dart';

/// Câmera com a orientação do passo pedido (prova de vida).
class StepViewfinder extends StatelessWidget {
  const StepViewfinder({super.key, required this.step, required this.current, required this.total, this.preview});

  final ChallengeStep step;
  final int current;
  final int total;
  final Widget? preview;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Column(
      children: [
        Expanded(
          child: ClipRRect(borderRadius: BorderRadius.circular(24), child: preview ?? const SizedBox.expand()),
        ),
        const SizedBox(height: 16),
        Text(step.instruction(l10n), style: theme.textTheme.titleLarge, textAlign: TextAlign.center),
        Text(l10n.faceStepProgress(current, total), style: theme.textTheme.bodySmall),
      ],
    );
  }
}

extension ChallengeStepText on ChallengeStep {
  String instruction(AppLocalizations l10n) => switch (this) {
    ChallengeStep.center => l10n.faceStepCenter,
    ChallengeStep.turnLeft => l10n.faceStepTurnLeft,
    ChallengeStep.turnRight => l10n.faceStepTurnRight,
  };
}
