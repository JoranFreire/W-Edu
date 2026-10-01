import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../agenda_providers.dart';
import '../widgets/agenda_lista.dart';

/// Agenda escolar do aluno: tarefas, provas, eventos e avisos das turmas dele.
class AgendaScreen extends ConsumerWidget {
  const AgendaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Agenda escolar')),
      body: AgendaLista(
        valor: ref.watch(minhaAgendaProvider),
        onRecarregar: () => ref.refresh(minhaAgendaProvider.future),
      ),
    );
  }
}
