import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/agenda_item.dart';
import 'agenda_item_card.dart';

/// Lista da agenda (do aluno ou de um dependente), com os estados de carregamento.
class AgendaList extends StatelessWidget {
  const AgendaList({super.key, required this.value, required this.onRefresh});

  final AsyncValue<List<AgendaItem>> value;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) => RemoteList<AgendaItem>(
    value: value,
    onRefresh: onRefresh,
    emptyText: context.l10n.agendaEmpty,
    emptyIcon: Icons.event_available_rounded,
    itemBuilder: (context, item) => AgendaItemCard(item: item),
  );
}
