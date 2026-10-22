import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/network_providers.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../../attendance/attendance_providers.dart';
import '../../auth/auth_providers.dart';
import '../widgets/role_label.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final l10n = context.l10n;
    final roles = user.roles.map((role) => roleLabel(role, l10n)).join(', ');

    return Scaffold(
      appBar: AppBar(title: Text(l10n.profileTitle)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DetailSection(
            title: user.name,
            children: [
              DetailRow(l10n.profileEmail, user.email),
              DetailRow(l10n.profileRole(user.roles.length), roles),
              DetailRow(l10n.profileInstitution, user.institution.name),
            ],
          ),
          if (ref.watch(personaBaseUrlProvider) != null) ...[
            const SizedBox(height: 16),
            Card(
              child: ListTile(
                leading: const Icon(Icons.face_retouching_natural),
                title: Text(l10n.profileFaceRecognition),
                subtitle: Text(l10n.profileFaceRecognitionHint),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go(Routes.biometrics),
              ),
            ),
          ],
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: () => _confirmSignOut(context, ref),
            icon: const Icon(Icons.logout_rounded),
            label: Text(l10n.signOut),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmSignOut(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    // Fotos de chamada ainda não enviadas são apagadas ao sair: avisa antes.
    final notUploaded = ref.read(currentUserProvider).teaches
        ? (await ref.read(attendanceQueueProvider).list()).where((a) => !a.isUploaded).length
        : 0;
    if (!context.mounted) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.signOutTitle),
        content: Text([l10n.signOutBody, if (notUploaded > 0) l10n.signOutPendingAttendance(notUploaded)].join('\n\n')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(l10n.cancel)),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: Text(l10n.signOut)),
        ],
      ),
    );
    if (confirmed == true) await ref.read(authProvider.notifier).signOut();
  }
}
