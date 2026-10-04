import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/agenda_item.dart';

class AgendaItemCard extends StatelessWidget {
  const AgendaItemCard({super.key, required this.item});

  final AgendaItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final detail = [item.classGroup, if (item.subject != null) item.subject!].join(' · ');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                AppBadge(item.kind.label(context.l10n), color: item.kind.color),
                const Spacer(),
                Text(formatLongDay(item.date), style: theme.textTheme.labelMedium),
              ],
            ),
            const SizedBox(height: 8),
            Text(item.title, style: theme.textTheme.titleSmall),
            if (item.description != null && item.description!.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(item.description!, style: theme.textTheme.bodyMedium),
            ],
            const SizedBox(height: 6),
            Text(detail, style: theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          ],
        ),
      ),
    );
  }
}

extension AgendaItemKindText on AgendaItemKind {
  String label(AppLocalizations l10n) => switch (this) {
    AgendaItemKind.homework => l10n.agendaKindHomework,
    AgendaItemKind.test => l10n.agendaKindTest,
    AgendaItemKind.event => l10n.agendaKindEvent,
    AgendaItemKind.notice => l10n.agendaKindNotice,
  };
}
