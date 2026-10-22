import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/network/network_providers.dart';
import '../../../l10n/l10n.dart';
import '../../agenda/agenda_providers.dart';
import '../../auth/auth_providers.dart';
import '../../auth/data/user.dart';
import '../../benefits/benefits_providers.dart';
import '../../dependents/dependents_providers.dart';
import '../../materials/materials_providers.dart';
import '../../notices/notices_providers.dart';
import '../widgets/home_summaries.dart';

/// Resumo do dia: avisos sem ler e, conforme os papéis, a próxima atividade e os dependentes.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final faceAttendance = user.teaches && ref.watch(personaBaseUrlProvider) != null;

    return Scaffold(
      appBar: AppBar(title: Text(user.institution.name)),
      body: RefreshIndicator(
        onRefresh: () => _refresh(ref, user),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(context.l10n.homeGreeting(user.firstName), style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 16),
            const NoticesSummary(),
            if (user.isStudent) ...const [AgendaSummary(), BenefitsSummary()],
            if (faceAttendance) const AttendanceSummary(),
            if (user.canRequestMaterials) const MaterialsSummary(),
            if (user.isGuardian) const DependentsSummary(),
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
}
