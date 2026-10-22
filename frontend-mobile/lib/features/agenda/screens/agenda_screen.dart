import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../l10n/l10n.dart';
import '../agenda_providers.dart';
import '../widgets/agenda_list.dart';

/// Agenda escolar do aluno: tarefas, provas, eventos e avisos das turmas dele.
class AgendaScreen extends ConsumerWidget {
  const AgendaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.agendaTitle)),
      body: AgendaList(value: ref.watch(myAgendaProvider), onRefresh: () => ref.refreshFromApi(myAgendaProvider, AgendaCacheKeys.mine)),
    );
  }
}
