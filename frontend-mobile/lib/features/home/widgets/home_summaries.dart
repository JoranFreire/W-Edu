import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../agenda/agenda_providers.dart';
import '../../agenda/data/agenda_item.dart';
import '../../attendance/attendance_providers.dart';
import '../../benefits/benefits_providers.dart';
import '../../dependents/dependents_providers.dart';
import '../../materials/materials_providers.dart';
import '../../notices/notices_providers.dart';
import 'summary_card.dart';
import 'summary_text.dart';

/// Os resumos do início, um por área. Cada um já vem com o espaço acima dele,
/// para que um resumo que não aparece (ex.: sem benefícios) não deixe buraco.
class _Spaced extends StatelessWidget {
  const _Spaced(this.child);

  final Widget child;

  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.only(top: 12), child: child);
}

class NoticesSummary extends ConsumerWidget {
  const NoticesSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return SummaryCard(
      icon: Icons.notifications_rounded,
      title: l10n.noticesTitle,
      value: summaryText(ref.watch(unreadNoticesProvider), l10n, (count) => count == 0 ? l10n.homeAllRead : l10n.homeUnread(count)),
      onTap: () => context.go(Routes.notices),
    );
  }
}

class AgendaSummary extends ConsumerWidget {
  const AgendaSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return _Spaced(SummaryCard(
      icon: Icons.event_note_rounded,
      title: l10n.homeNextOnAgenda,
      value: summaryText(ref.watch(myAgendaProvider), l10n, (items) => _next(items, l10n)),
      onTap: () => context.go(Routes.agenda),
    ));
  }

  /// O primeiro item de hoje em diante.
  String _next(List<AgendaItem> items, AppLocalizations l10n) {
    final today = DateUtils.dateOnly(DateTime.now());
    final upcoming = items.where((item) => !item.date.isBefore(today)).firstOrNull;
    return upcoming == null ? l10n.homeNothingAhead : l10n.homeNextItem(upcoming.title, formatDay(upcoming.date));
  }
}

/// Só aparece se a instituição já liberou algum benefício ao aluno.
class BenefitsSummary extends ConsumerWidget {
  const BenefitsSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final benefits = ref.watch(myBenefitsProvider).value ?? const [];
    if (benefits.isEmpty) return const SizedBox.shrink();
    final l10n = context.l10n;
    return _Spaced(SummaryCard(
      icon: Icons.redeem_rounded,
      title: l10n.benefitsTitle,
      value: toPickUpText(benefits.where((b) => b.isReadyForPickup).length, l10n),
      onTap: () => context.go(Routes.benefits),
    ));
  }
}

class AttendanceSummary extends ConsumerWidget {
  const AttendanceSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final pending = ref.watch(pendingAttendancesProvider).value?.length ?? 0;
    return _Spaced(SummaryCard(
      icon: Icons.how_to_reg_rounded,
      title: l10n.homeFaceAttendance,
      value: pending == 0 ? l10n.homeAttendanceHint : l10n.homeAttendancePending(pending),
      onTap: () => context.go(Routes.attendance),
    ));
  }
}

class MaterialsSummary extends ConsumerWidget {
  const MaterialsSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return _Spaced(SummaryCard(
      icon: Icons.inventory_2_rounded,
      title: l10n.materialsTitle,
      value: summaryText(
        ref.watch(myMaterialRequestsProvider),
        l10n,
        (requests) => toPickUpText(requests.where((r) => r.isReadyForPickup).length, l10n),
      ),
      onTap: () => context.go(Routes.materials),
    ));
  }
}

class DependentsSummary extends ConsumerWidget {
  const DependentsSummary({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return _Spaced(SummaryCard(
      icon: Icons.family_restroom_rounded,
      title: l10n.tabDependents,
      value: summaryText(
        ref.watch(dependentsProvider),
        l10n,
        (dependents) => dependents.isEmpty ? l10n.homeNoDependents : dependents.map((d) => d.firstName).join(', '),
      ),
      onTap: () => context.go(Routes.dependents),
    ));
  }
}
