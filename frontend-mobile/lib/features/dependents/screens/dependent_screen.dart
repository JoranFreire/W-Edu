import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/network/network_providers.dart';
import '../../../l10n/l10n.dart';
import '../../agenda/agenda_providers.dart';
import '../../agenda/widgets/agenda_list.dart';
import '../../benefits/benefits_providers.dart';
import '../../benefits/widgets/benefits_list.dart';
import '../../biometrics/widgets/dependent_consents.dart';
import '../../report_card/report_card_providers.dart';
import '../../report_card/widgets/report_card_list.dart';
import '../dependents_providers.dart';

/// Um dependente: boletim, agenda da turma, benefícios (com o QR para a retirada) e, com o
/// Persona configurado, as autorizações de uso do rosto (login e catraca) do menor.
class DependentScreen extends ConsumerWidget {
  const DependentScreen({super.key, required this.studentId});

  final String studentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final dependents = ref.watch(dependentsProvider).value ?? const [];
    final name = dependents.where((d) => d.studentId == studentId).map((d) => d.name).firstOrNull ?? l10n.dependentFallbackName;
    final withFace = ref.watch(personaBaseUrlProvider) != null;
    return DefaultTabController(
      length: withFace ? 4 : 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(name),
          bottom: TabBar(
            isScrollable: withFace,
            tabs: [
              Tab(text: l10n.tabReportCard),
              Tab(text: l10n.tabAgenda),
              Tab(text: l10n.dependentTabBenefits),
              if (withFace) Tab(text: l10n.dependentTabFace),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            ReportCardList(
              value: ref.watch(dependentReportCardProvider(studentId)),
              onRefresh: () => ref.refreshFromApi(dependentReportCardProvider(studentId), ReportCardCacheKeys.ofDependent(studentId)),
            ),
            AgendaList(
              value: ref.watch(dependentAgendaProvider(studentId)),
              onRefresh: () => ref.refreshFromApi(dependentAgendaProvider(studentId), AgendaCacheKeys.ofDependent(studentId)),
            ),
            BenefitsList(
              value: ref.watch(dependentBenefitsProvider(studentId)),
              onRefresh: () => ref.refreshFromApi(dependentBenefitsProvider(studentId), BenefitCacheKeys.ofDependent(studentId)),
            ),
            if (withFace) DependentConsents(studentId: studentId),
          ],
        ),
      ),
    );
  }
}
