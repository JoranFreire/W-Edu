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
            _PeriodGrades(subject: subject),
            const Divider(height: 24),
            _Totals(subject: subject),
          ],
        ),
      ),
    );
  }
}

TextStyle? _labelStyle(ThemeData theme) => theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant);

/// Média e faltas de cada etapa.
class _PeriodGrades extends StatelessWidget {
  const _PeriodGrades({required this.subject});

  final ReportCardSubject subject;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final label = _labelStyle(theme);
    if (subject.periods.isEmpty) return Text(l10n.reportCardNoPeriods, style: label);
    return Wrap(
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
    );
  }
}

/// Nota final, recuperação, frequência e a média para passar.
class _Totals extends StatelessWidget {
  const _Totals({required this.subject});

  final ReportCardSubject subject;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Wrap(
      spacing: 16,
      runSpacing: 4,
      children: [
        if (subject.finalGrade != null) Text(l10n.reportCardFinalGrade(formatGrade(subject.finalGrade!))),
        if (subject.recoveryScore != null) Text(l10n.reportCardRecovery(formatGrade(subject.recoveryScore!))),
        if (subject.attendanceRate != null) Text(l10n.reportCardAttendance(formatPercent(subject.attendanceRate!))),
        Text(l10n.reportCardPassingGrade(formatGrade(subject.passingGrade)), style: _labelStyle(Theme.of(context))),
      ],
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
