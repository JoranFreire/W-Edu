import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../attendance_providers.dart';
import '../data/pending_attendance.dart';

/// Chamadas fotografadas sem rede: enviadas sozinhas ao abrir a tela e ao voltar para o app; as já
/// enviadas abrem a revisão. Descartar apaga as fotos do aparelho.
class PendingAttendanceSection extends ConsumerStatefulWidget {
  const PendingAttendanceSection({super.key});

  @override
  ConsumerState<PendingAttendanceSection> createState() => _PendingAttendanceSectionState();
}

class _PendingAttendanceSectionState extends ConsumerState<PendingAttendanceSection> {
  late final AppLifecycleListener _lifecycle;
  bool _uploading = false;

  @override
  void initState() {
    super.initState();
    _lifecycle = AppLifecycleListener(onResume: _upload);
  }

  @override
  void dispose() {
    _lifecycle.dispose();
    super.dispose();
  }

  Future<void> _upload() async {
    if (_uploading) return;
    setState(() => _uploading = true);
    try {
      await ref.read(pendingAttendancesProvider.notifier).upload();
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Future<void> _discard(PendingAttendance attendance) async {
    final l10n = context.l10n;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(l10n.pendingDiscardTitle),
        content: Text(l10n.pendingDiscardBody(attendance.title)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: Text(l10n.keep)),
          FilledButton(onPressed: () => Navigator.pop(dialogContext, true), child: Text(l10n.discard)),
        ],
      ),
    );
    if (confirmed ?? false) await ref.read(pendingAttendancesProvider.notifier).discard(attendance.id);
  }

  @override
  Widget build(BuildContext context) {
    final pending = ref.watch(pendingAttendancesProvider).value ?? const [];
    if (pending.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final toUpload = pending.where((a) => !a.isUploaded).length;
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ListTile(
              leading: const Icon(Icons.cloud_upload_outlined),
              title: Text(l10n.pendingStored(pending.length), style: theme.textTheme.titleSmall),
              trailing: toUpload == 0
                  ? null
                  : _uploading
                  ? const SizedBox.square(dimension: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : TextButton(onPressed: _upload, child: Text(l10n.sendNow)),
            ),
            for (final attendance in pending)
              ListTile(
                title: Text(attendance.title),
                subtitle: Text(
                  l10n.pendingSummary(
                    attendance.photos.length,
                    formatDayTime(attendance.createdAt),
                    attendance.isUploaded ? l10n.pendingReady : l10n.pendingWaiting,
                  ),
                ),
                onTap: attendance.isUploaded
                    ? () => context.go(Routes.attendanceMeeting(attendance.offeringId, attendance.meetingId, pendingId: attendance.id))
                    : null,
                trailing: IconButton(
                  tooltip: l10n.discard,
                  icon: const Icon(Icons.delete_outline_rounded),
                  onPressed: () => _discard(attendance),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
