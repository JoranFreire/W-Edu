import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/format/dates.dart';
import '../../../core/network/network_providers.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../agenda/agenda_providers.dart';
import '../../agenda/data/agenda_item.dart';
import '../../attendance/attendance_providers.dart';
import '../../auth/auth_providers.dart';
import '../../auth/data/user.dart';
import '../../benefits/benefits_providers.dart';
import '../../dependents/dependents_providers.dart';
import '../../materials/materials_providers.dart';
import '../../notices/notices_providers.dart';
import '../widgets/summary_card.dart';

/// Resumo do dia: avisos sem ler e, conforme os papéis, a próxima atividade e os dependentes.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final unread = ref.watch(unreadNoticesProvider);
    final theme = Theme.of(context);
    final l10n = context.l10n;

    String summary<T>(AsyncValue<T> value, String Function(T data) text) => switch (value) {
      AsyncData(:final value) => text(value),
      AsyncError() => l10n.homeTapToSee,
      _ => '…',
    };

    return Scaffold(
      appBar: AppBar(title: Text(user.institution.name)),
      body: RefreshIndicator(
        onRefresh: () => _refresh(ref, user),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(l10n.homeGreeting(user.firstName), style: theme.textTheme.headlineSmall),
            const SizedBox(height: 16),
            SummaryCard(
              icon: Icons.notifications_rounded,
              title: l10n.noticesTitle,
              value: summary(unread, (count) => count == 0 ? l10n.homeAllRead : l10n.homeUnread(count)),
              onTap: () => context.go(Routes.notices),
            ),
            if (user.isStudent) ...[
              const SizedBox(height: 12),
              SummaryCard(
                icon: Icons.event_note_rounded,
                title: l10n.homeNextOnAgenda,
                value: summary(ref.watch(myAgendaProvider), (items) => _next(items, l10n)),
                onTap: () => context.go(Routes.agenda),
              ),
              ..._benefits(context, ref, l10n),
            ],
            if (user.teaches && ref.watch(personaBaseUrlProvider) != null) ...[
              const SizedBox(height: 12),
              SummaryCard(
                icon: Icons.how_to_reg_rounded,
                title: l10n.homeFaceAttendance,
                value: _pending(ref.watch(pendingAttendancesProvider).value?.length ?? 0, l10n),
                onTap: () => context.go(Routes.attendance),
              ),
            ],
            if (user.canRequestMaterials) ...[
              const SizedBox(height: 12),
              SummaryCard(
                icon: Icons.inventory_2_rounded,
                title: l10n.materialsTitle,
                value: summary(
                  ref.watch(myMaterialRequestsProvider),
                  (requests) => _toPickUp(requests.where((r) => r.isReadyForPickup).length, l10n),
                ),
                onTap: () => context.go(Routes.materials),
              ),
            ],
            if (user.isGuardian) ...[
              const SizedBox(height: 12),
              SummaryCard(
                icon: Icons.family_restroom_rounded,
                title: l10n.tabDependents,
                value: summary(
                  ref.watch(dependentsProvider),
                  (dependents) => dependents.isEmpty ? l10n.homeNoDependents : dependents.map((d) => d.firstName).join(', '),
                ),
                onTap: () => context.go(Routes.dependents),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// Puxar para atualizar: cada resumo direto da API; sem rede, fica o salvo.
  Future<void> _refresh(WidgetRef ref, User user) async {
    await [
      ref.refreshFromApi(unreadNoticesProvider, NoticeCacheKeys.summary),
      if (user.isStudent) ref.refreshFromApi(myAgendaProvider, AgendaCacheKeys.mine),
      if (user.isStudent) ref.refreshFromApi(myBenefitsProvider, BenefitCacheKeys.mine),
      if (user.isGuardian) ref.refreshFromApi(dependentsProvider, DependentCacheKeys.list),
      if (user.canRequestMaterials) ref.refreshFromApi(myMaterialRequestsProvider, MaterialCacheKeys.mine),
    ].map((refresh) => refresh.then<void>((_) {}, onError: (_) {})).wait;
  }

  /// Só aparece se a instituição já liberou algum benefício ao aluno.
  List<Widget> _benefits(BuildContext context, WidgetRef ref, AppLocalizations l10n) {
    final benefits = ref.watch(myBenefitsProvider).value ?? const [];
    if (benefits.isEmpty) return const [];
    return [
      const SizedBox(height: 12),
      SummaryCard(
        icon: Icons.redeem_rounded,
        title: l10n.benefitsTitle,
        value: _toPickUp(benefits.where((b) => b.isReadyForPickup).length, l10n),
        onTap: () => context.go(Routes.benefits),
      ),
    ];
  }

  String _pending(int count, AppLocalizations l10n) => count == 0 ? l10n.homeAttendanceHint : l10n.homeAttendancePending(count);

  String _toPickUp(int count, AppLocalizations l10n) => count == 0 ? l10n.homeNothingToPickUp : l10n.homeToPickUp(count);

  /// O primeiro item de hoje em diante.
  String _next(List<AgendaItem> items, AppLocalizations l10n) {
    final today = DateUtils.dateOnly(DateTime.now());
    final upcoming = items.where((item) => !item.date.isBefore(today)).firstOrNull;
    return upcoming == null ? l10n.homeNothingAhead : l10n.homeNextItem(upcoming.title, formatDay(upcoming.date));
  }
}
