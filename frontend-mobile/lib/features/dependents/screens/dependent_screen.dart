import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/network/network_providers.dart';
import '../../agenda/agenda_providers.dart';
import '../../agenda/widgets/agenda_list.dart';
import '../../report_card/report_card_providers.dart';
import '../../benefits/benefits_providers.dart';
import '../../benefits/widgets/benefits_list.dart';
import '../../biometrics/widgets/dependent_consents.dart';
import '../../report_card/widgets/report_card_list.dart';
import '../dependents_providers.dart';

/// Um dependente: boletim, agenda da turma, benefícios (com o QR para a retirada) e, com o
/// Persona configurado, as autorizações de uso do rosto (login e catraca) do menor.
class DependenteScreen extends ConsumerWidget {
  const DependenteScreen({super.key, required this.alunoId});

  final String alunoId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dependentes = ref.watch(dependentesProvider).value ?? const [];
    final nome = dependentes.where((d) => d.alunoId == alunoId).map((d) => d.nome).firstOrNull ?? 'Dependente';
    final comRosto = ref.watch(personaBaseUrlProvider) != null;
    return DefaultTabController(
      length: comRosto ? 4 : 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(nome),
          bottom: TabBar(
            isScrollable: comRosto,
            tabs: [const Tab(text: 'Boletim'), const Tab(text: 'Agenda'), const Tab(text: 'Benefícios'), if (comRosto) const Tab(text: 'Rosto')],
          ),
        ),
        body: TabBarView(
          children: [
            BoletimLista(
              valor: ref.watch(boletimDoDependenteProvider(alunoId)),
              onRecarregar: () => ref.atualizarDaApi(boletimDoDependenteProvider(alunoId), ChavesBoletim.doDependente(alunoId)),
            ),
            AgendaLista(
              valor: ref.watch(agendaDoDependenteProvider(alunoId)),
              onRecarregar: () => ref.atualizarDaApi(agendaDoDependenteProvider(alunoId), ChavesAgenda.doDependente(alunoId)),
            ),
            BeneficiosLista(
              valor: ref.watch(beneficiosDoDependenteProvider(alunoId)),
              onRecarregar: () => ref.atualizarDaApi(beneficiosDoDependenteProvider(alunoId), ChavesBeneficios.doDependente(alunoId)),
            ),
            if (comRosto) AutorizacoesDependente(alunoId: alunoId),
          ],
        ),
      ),
    );
  }
}
