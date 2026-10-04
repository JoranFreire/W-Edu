import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../shared/ds/ds.dart';
import '../data/agenda_item.dart';

class ItemAgendaCard extends StatelessWidget {
  const ItemAgendaCard({super.key, required this.item});

  final ItemAgenda item;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final detalhe = [item.turma, if (item.disciplina != null) item.disciplina!].join(' · ');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                AppBadge(item.tipo.nome, cor: item.tipo.cor),
                const Spacer(),
                Text(formatarDiaPorExtenso(item.data), style: tema.textTheme.labelMedium),
              ],
            ),
            const SizedBox(height: 8),
            Text(item.titulo, style: tema.textTheme.titleSmall),
            if (item.descricao != null && item.descricao!.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(item.descricao!, style: tema.textTheme.bodyMedium),
            ],
            const SizedBox(height: 6),
            Text(detalhe, style: tema.textTheme.labelSmall?.copyWith(color: tema.colorScheme.onSurfaceVariant)),
          ],
        ),
      ),
    );
  }
}
