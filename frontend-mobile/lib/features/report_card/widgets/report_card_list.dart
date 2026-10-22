import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/report_card.dart';
import 'subject_card.dart';

/// Boletim (do aluno ou de um dependente), com os estados de carregamento.
class ReportCardList extends StatelessWidget {
  const ReportCardList({super.key, required this.value, required this.onRefresh});

  final AsyncValue<List<ReportCardSubject>> value;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) => RemoteList<ReportCardSubject>(
    value: value,
    onRefresh: onRefresh,
    emptyText: context.l10n.reportCardEmpty,
    emptyIcon: Icons.grading_rounded,
    itemBuilder: (context, subject) => SubjectCard(subject: subject),
  );
}
