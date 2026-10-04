import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/ds/ds.dart';
import '../data/agenda_item.dart';
import 'agenda_item_card.dart';

/// Lista da agenda (do aluno ou de um dependente), com os estados de carregamento.
class AgendaLista extends StatelessWidget {
  const AgendaLista({super.key, required this.valor, required this.onRecarregar});

  final AsyncValue<List<ItemAgenda>> valor;
  final Future<void> Function() onRecarregar;

  @override
  Widget build(BuildContext context) => ListaRemota<ItemAgenda>(
        valor: valor,
        onRecarregar: onRecarregar,
        textoVazio: 'Nada na agenda por enquanto.',
        iconeVazio: Icons.event_available_rounded,
        itemBuilder: (context, item) => ItemAgendaCard(item: item),
      );
}
