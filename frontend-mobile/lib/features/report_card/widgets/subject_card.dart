import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../shared/ds/ds.dart';
import '../data/report_card.dart';

/// Uma disciplina: média de cada etapa, faltas, frequência e o resultado final.
class DisciplinaCard extends StatelessWidget {
  const DisciplinaCard({super.key, required this.disciplina});

  final DisciplinaBoletim disciplina;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final rotulo = tema.textTheme.labelSmall?.copyWith(color: tema.colorScheme.onSurfaceVariant);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(disciplina.nome, style: tema.textTheme.titleSmall)),
                if (disciplina.finalizada) AppBadge(disciplina.resultado.nome, cor: disciplina.resultado.cor),
              ],
            ),
            const SizedBox(height: 12),
            if (disciplina.etapas.isEmpty)
              Text('Nenhuma etapa fechada ainda.', style: rotulo)
            else
              Wrap(
                spacing: 16,
                runSpacing: 8,
                children: [
                  for (final etapa in disciplina.etapas)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(etapa.nome, style: rotulo),
                        Text(etapa.media == null ? '—' : formatarNota(etapa.media!), style: tema.textTheme.titleMedium),
                        Text('${etapa.faltas} falta${etapa.faltas == 1 ? '' : 's'}', style: rotulo),
                      ],
                    ),
                ],
              ),
            const Divider(height: 24),
            Wrap(
              spacing: 16,
              runSpacing: 4,
              children: [
                if (disciplina.notaFinal != null) Text('Média final: ${formatarNota(disciplina.notaFinal!)}'),
                if (disciplina.recuperacao != null) Text('Recuperação: ${formatarNota(disciplina.recuperacao!)}'),
                if (disciplina.frequencia != null) Text('Frequência: ${formatarPorcentagem(disciplina.frequencia!)}'),
                Text('Média para aprovar: ${formatarNota(disciplina.mediaAprovacao)}', style: rotulo),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
