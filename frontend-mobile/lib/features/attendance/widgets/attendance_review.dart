import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';
import '../attendance_flow.dart';
import '../data/attendance_result.dart';
import 'attendance_labels.dart';
import 'persona_image.dart';

/// Revisão antes de gravar: reconhecidos já marcados; os "para conferir" mostram o rosto achado ao
/// lado da foto do cadastro; os sem autorização o professor marca à mão.
class AttendanceReview extends StatelessWidget {
  const AttendanceReview({super.key, required this.step, required this.onToggle, required this.onConfirm});

  final AttendanceReviewing step;
  final void Function(String personId) onToggle;
  final VoidCallback onConfirm;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final result = step.result;
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(vertical: 8),
            children: [
              for (final outcome in PhotoOutcome.values)
                if (result.withOutcome(outcome).isNotEmpty) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
                    child: Text(
                      l10n.outcomeSection(outcome.label(l10n), result.withOutcome(outcome).length),
                      style: theme.textTheme.titleSmall,
                    ),
                  ),
                  for (final student in result.withOutcome(outcome))
                    CheckboxListTile(
                      value: step.present.contains(student.personId),
                      onChanged: (_) => onToggle(student.personId),
                      title: Text(student.name),
                      subtitle: outcome == PhotoOutcome.uncertain
                          ? Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Row(
                                children: [
                                  PersonaImage(path: student.cropUrl, caption: l10n.inThePhoto),
                                  const SizedBox(width: 12),
                                  PersonaImage(path: student.enrollmentPhotoUrl, caption: l10n.enrollmentPhoto),
                                ],
                              ),
                            )
                          : null,
                    ),
                ],
            ],
          ),
        ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton(onPressed: onConfirm, child: Text(l10n.attendanceConfirm(step.present.length, result.students.length))),
            ),
          ),
        ),
      ],
    );
  }
}
