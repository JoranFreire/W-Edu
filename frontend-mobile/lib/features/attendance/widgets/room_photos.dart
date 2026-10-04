import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';
import '../attendance_flow.dart';
import '../data/attendance_result.dart';
import 'attendance_labels.dart';

/// Fotos da sala: um ângulo por vez (esquerda, centro, direita). Pelo menos uma para analisar.
class RoomPhotos extends StatelessWidget {
  const RoomPhotos({super.key, required this.step, required this.preview, required this.onTakePhoto, required this.onAnalyze});

  final AttendancePhotographing step;
  final Widget? preview;
  final void Function(PhotoAngle angle) onTakePhoto;
  final VoidCallback onAnalyze;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final session = step.session;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            session == null
                ? l10n.attendanceOfflineHint
                : l10n.attendanceWithConsent(session.withConsent) +
                      (session.withoutConsent > 0 ? l10n.attendanceWithoutConsent(session.withoutConsent) : ''),
            style: theme.textTheme.bodyMedium,
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: preview ?? const ColoredBox(color: Colors.black),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              for (final angle in PhotoAngle.values)
                FilledButton.tonalIcon(
                  onPressed: step.sending == null ? () => onTakePhoto(angle) : null,
                  icon: step.sending == angle
                      ? const SizedBox.square(dimension: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : Icon(step.taken.contains(angle) ? Icons.check_circle_rounded : Icons.photo_camera_rounded),
                  label: Text(angle.label(l10n)),
                ),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: step.taken.isNotEmpty && step.sending == null ? onAnalyze : null,
            child: Text(session == null ? l10n.attendanceStore(step.taken.length) : l10n.attendanceAnalyze(step.taken.length)),
          ),
        ],
      ),
    );
  }
}
