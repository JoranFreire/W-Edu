import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/observar_area.dart';
import '../../agenda/agenda_providers.dart';
import '../../agenda/widgets/agenda_lista.dart';
import '../../boletim/boletim_providers.dart';
import '../../boletim/widgets/boletim_lista.dart';
import '../dependentes_providers.dart';

/// Um dependente: boletim e agenda da turma dele.
class DependenteScreen extends ConsumerWidget {
  const DependenteScreen({super.key, required this.alunoId});

  final String alunoId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dependentes = ref.watch(dependentesProvider).value ?? const [];
    final nome = dependentes.where((d) => d.alunoId == alunoId).map((d) => d.nome).firstOrNull ?? 'Dependente';
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: Text(nome),
          bottom: const TabBar(tabs: [Tab(text: 'Boletim'), Tab(text: 'Agenda')]),
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
          ],
        ),
      ),
    );
  }
}
