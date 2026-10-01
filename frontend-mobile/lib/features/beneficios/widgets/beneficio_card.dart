import 'package:flutter/material.dart';

import '../../../core/format/datas.dart';
import '../../../shared/ds/ds.dart';
import '../data/beneficio.dart';
import 'qr_beneficio_view.dart';

class BeneficioCard extends StatelessWidget {
  const BeneficioCard({super.key, required this.beneficio});

  final Beneficio beneficio;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final situacao = beneficio.situacao();
    final quando = switch (situacao) {
      SituacaoBeneficio.retirado when beneficio.retiradoEm != null => 'Retirado em ${formatarDia(beneficio.retiradoEm!.toLocal())}',
      SituacaoBeneficio.liberado when beneficio.validoAte != null => 'Retire até ${formatarDia(beneficio.validoAte!)}',
      _ => 'Liberado em ${formatarDia(beneficio.liberadoEm.toLocal())}',
    };
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: beneficio.paraRetirar ? () => abrirQrDoBeneficio(context, beneficio) : null,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(beneficio.tipo.icone, color: tema.colorScheme.primary),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    AppBadge(situacao.nome, cor: situacao.cor),
                    const SizedBox(height: 8),
                    Text('${beneficio.item} × ${beneficio.quantidade}', style: tema.textTheme.titleSmall),
                    Text(beneficio.tipo.nome, style: tema.textTheme.bodySmall),
                    const SizedBox(height: 4),
                    Text(quando, style: tema.textTheme.labelSmall?.copyWith(color: tema.colorScheme.onSurfaceVariant)),
                  ],
                ),
              ),
              if (beneficio.paraRetirar)
                FilledButton.tonalIcon(
                  onPressed: () => abrirQrDoBeneficio(context, beneficio),
                  icon: const Icon(Icons.qr_code_2_rounded),
                  label: const Text('Mostrar QR'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
