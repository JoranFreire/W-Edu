import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/report_card.dart';

/// Uma disciplina: média de cada etapa, faltas, frequência e o resultado final.
class SubjectCard extends StatelessWidget {
  const SubjectCard({super.key, required this.subject});

  final ReportCardSubject subject;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final label = theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(subject.name, style: theme.textTheme.titleSmall)),
                if (subject.finalized) AppBadge(subject.result.label(l10n), color: subject.result.color),
              ],
            ),
            const SizedBox(height: 12),
            if (subject.periods.isEmpty)
              Text(l10n.reportCardNoPeriods, style: label)
            else
              Wrap(
                spacing: 16,
                runSpacing: 8,
                children: [
                  for (final period in subject.periods)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(period.name, style: label),
                        Text(period.average == null ? '—' : formatGrade(period.average!), style: theme.textTheme.titleMedium),
                        Text(l10n.reportCardAbsences(period.absences), style: label),
                      ],
                    ),
                ],
              ),
            const Divider(height: 24),
            Wrap(
              spacing: 16,
              runSpacing: 4,
              children: [
                if (subject.finalGrade != null) Text(l10n.reportCardFinalGrade(formatGrade(subject.finalGrade!))),
                if (subject.recoveryScore != null) Text(l10n.reportCardRecovery(formatGrade(subject.recoveryScore!))),
                if (subject.attendanceRate != null) Text(l10n.reportCardAttendance(formatPercent(subject.attendanceRate!))),
                Text(l10n.reportCardPassingGrade(formatGrade(subject.passingGrade)), style: label),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

extension SubjectResultText on SubjectResult {
  String label(AppLocalizations l10n) => switch (this) {
    SubjectResult.inProgress => l10n.subjectInProgress,
    SubjectResult.recovery => l10n.subjectRecovery,
    SubjectResult.approved => l10n.subjectApproved,
    SubjectResult.failed => l10n.subjectFailed,
    SubjectResult.failedAttendance => l10n.subjectFailedAttendance,
  };
}
