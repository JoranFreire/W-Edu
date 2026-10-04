import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/api_error.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../attendance_flow.dart';
import '../widgets/attendance_labels.dart';
import '../widgets/attendance_review.dart';
import '../widgets/room_photos.dart';

/// Chamada facial de um encontro: fotos da sala → análise no Persona → revisão → confirmação.
class AttendanceScreen extends ConsumerWidget {
  const AttendanceScreen({super.key, required this.offeringId, required this.meetingId, this.pendingId});

  final String offeringId;
  final String meetingId;

  /// Chamada que veio da fila (fotografada sem rede).
  final String? pendingId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = (offeringId: offeringId, meetingId: meetingId, pendingId: pendingId);
    final step = ref.watch(attendanceFlowProvider(key));
    final flow = ref.read(attendanceFlowProvider(key).notifier);
    final l10n = context.l10n;
    final theme = Theme.of(context);
    void backToMeetings() => context.go(Routes.attendanceOffering(offeringId));

    Future<void> warnIfFailed(Future<Object?> action, String fallback) async {
      final messenger = ScaffoldMessenger.of(context);
      final error = await action;
      if (error != null) messenger.showSnackBar(SnackBar(content: Text(apiErrorMessage(error, l10n, fallback: fallback))));
    }

    return Scaffold(
      appBar: AppBar(title: Text(l10n.attendanceTitle)),
      body: switch (step) {
        AttendanceOpening() => _Wait(l10n.attendanceOpening),
        AttendanceOffline() => _Outcome(
          icon: Icons.wifi_off_rounded,
          text: l10n.attendanceOffline,
          action: (l10n.attendancePhotographLater, flow.photographOffline),
          onBack: backToMeetings,
        ),
        AttendancePhotosSaved(:final count) => _Outcome(
          icon: Icons.cloud_upload_outlined,
          text: l10n.attendancePhotosSaved(count),
          onBack: () => context.go(Routes.attendance),
        ),
        AttendanceProcessing() => _Wait(l10n.attendanceAnalyzing),
        AttendanceConfirming() => _Wait(l10n.attendanceSaving),
        AttendancePhotographing() => RoomPhotos(
          step: step,
          preview: flow.camera?.preview(),
          onTakePhoto: (angle) => warnIfFailed(flow.takePhoto(angle), l10n.attendancePhotoFailed),
          onAnalyze: flow.analyze,
        ),
        AttendanceReviewing() => AttendanceReview(
          step: step,
          onToggle: flow.toggle,
          onConfirm: () => warnIfFailed(flow.confirm(), l10n.attendanceConfirmFailed),
        ),
        AttendanceConfirmed(:final present, :final total) => _Outcome(
          icon: Icons.task_alt_rounded,
          text: l10n.attendanceConfirmed(present, total),
          onBack: backToMeetings,
        ),
        AttendanceFailed() => _Outcome(
          icon: Icons.error_outline_rounded,
          text: step.message(l10n),
          color: theme.colorScheme.error,
          onBack: backToMeetings,
        ),
      },
    );
  }
}

class _Wait extends StatelessWidget {
  const _Wait(this.text);

  final String text;

  @override
  Widget build(BuildContext context) => Center(
    child: Column(mainAxisSize: MainAxisSize.min, children: [const LoadingView(), const SizedBox(height: 16), Text(text)]),
  );
}

class _Outcome extends StatelessWidget {
  const _Outcome({required this.icon, required this.text, required this.onBack, this.color, this.action});

  final IconData icon;
  final String text;
  final VoidCallback onBack;
  final Color? color;

  /// Ação principal opcional (rótulo, ação); o voltar vira secundário.
  final (String, VoidCallback)? action;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 72, color: color ?? theme.colorScheme.primary),
            const SizedBox(height: 16),
            Text(
              text,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyLarge?.copyWith(color: color),
            ),
            const SizedBox(height: 24),
            if (action case (final label, final run)) ...[
              FilledButton(onPressed: run, child: Text(label)),
              TextButton(onPressed: onBack, child: Text(l10n.back)),
            ] else
              FilledButton(onPressed: onBack, child: Text(l10n.attendanceBackToMeetings)),
          ],
        ),
      ),
    );
  }
}
