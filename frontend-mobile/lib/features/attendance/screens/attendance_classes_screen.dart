import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../attendance_providers.dart';
import '../data/teaching.dart';
import '../widgets/pending_attendance_section.dart';

/// Chamada facial: escolha a turma (só as que você ministra).
class AttendanceClassesScreen extends ConsumerWidget {
  const AttendanceClassesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.attendanceTitle)),
      body: RemoteList<TeachingOffering>(
        value: ref.watch(teachingOfferingsProvider),
        onRefresh: () => ref.refreshFromApi(teachingOfferingsProvider, TeachingCacheKeys.offerings),
        emptyText: l10n.attendanceNoClasses,
        emptyIcon: Icons.groups_outlined,
        header: const PendingAttendanceSection(),
        itemBuilder: (context, offering) => Card(
          child: ListTile(
            leading: const Icon(Icons.groups_rounded),
            title: Text(offering.name),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go(Routes.attendanceOffering(offering.id)),
          ),
        ),
      ),
    );
  }
}
