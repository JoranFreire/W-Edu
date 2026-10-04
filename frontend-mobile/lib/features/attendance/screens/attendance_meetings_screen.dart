import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../attendance_providers.dart';
import '../data/teaching.dart';

/// Encontros ainda abertos da turma, o de hoje primeiro.
class AttendanceMeetingsScreen extends ConsumerWidget {
  const AttendanceMeetingsScreen({super.key, required this.offeringId});

  final String offeringId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.attendanceChooseMeeting)),
      body: RemoteList<Meeting>(
        value: ref.watch(meetingsProvider(offeringId)),
        onRefresh: () => ref.refreshFromApi(meetingsProvider(offeringId), TeachingCacheKeys.meetings(offeringId)),
        emptyText: l10n.attendanceNoMeetings,
        emptyIcon: Icons.event_busy_outlined,
        itemBuilder: (context, meeting) => Card(
          child: ListTile(
            leading: const Icon(Icons.event_rounded),
            title: Text(meeting.title),
            subtitle: Text(formatDayTime(meeting.startsAt)),
            trailing: const Icon(Icons.photo_camera_rounded),
            onTap: () => context.go(Routes.attendanceMeeting(offeringId, meeting.id)),
          ),
        ),
      ),
    );
  }
}
