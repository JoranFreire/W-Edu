import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/notice.dart';
import '../notices_providers.dart';
import '../widgets/notice_card.dart';

class NoticesScreen extends ConsumerWidget {
  const NoticesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notices = ref.watch(noticesProvider);
    final notifier = ref.read(noticesProvider.notifier);
    final hasUnread = notices.value?.any((notice) => !notice.isRead) ?? false;
    final l10n = context.l10n;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.noticesTitle),
        actions: [if (hasUnread) TextButton(onPressed: notifier.markAllAsRead, child: Text(l10n.markAllAsRead))],
      ),
      body: RemoteList<Notice>(
        value: notices,
        onRefresh: notifier.reload,
        emptyText: l10n.noNotices,
        emptyIcon: Icons.notifications_none_rounded,
        itemBuilder: (context, notice) => NoticeCard(
          notice: notice,
          onTap: () {
            notifier.markAsRead(notice);
            _open(context, notice);
          },
        ),
      ),
    );
  }

  void _open(BuildContext context, Notice notice) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(notice.title, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(formatDayTime(notice.createdAt), style: Theme.of(context).textTheme.labelMedium),
              const SizedBox(height: 16),
              Text(notice.body, style: Theme.of(context).textTheme.bodyLarge),
            ],
          ),
        ),
      ),
    );
  }
}
