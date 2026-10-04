import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../data/notice.dart';

/// Um aviso na lista: não lido aparece em destaque, com o ponto da cor principal.
class NoticeCard extends StatelessWidget {
  const NoticeCard({super.key, required this.notice, required this.onTap});

  final Notice notice;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 6, right: 12),
                child: Icon(Icons.circle, size: 10, color: notice.isRead ? Colors.transparent : theme.colorScheme.primary),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      notice.title,
                      style: theme.textTheme.titleSmall?.copyWith(fontWeight: notice.isRead ? FontWeight.w500 : FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    Text(notice.body, maxLines: 2, overflow: TextOverflow.ellipsis, style: theme.textTheme.bodyMedium),
                    const SizedBox(height: 6),
                    Text(
                      formatDayTime(notice.createdAt),
                      style: theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
