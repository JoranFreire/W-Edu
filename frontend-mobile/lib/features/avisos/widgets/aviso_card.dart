import 'package:flutter/material.dart';

import '../../../core/format/datas.dart';
import '../data/aviso.dart';

/// Um aviso na lista: não lido aparece em destaque, com o ponto da cor principal.
class AvisoCard extends StatelessWidget {
  const AvisoCard({super.key, required this.aviso, required this.onTap});

  final Aviso aviso;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 6, right: 12),
                child: Icon(Icons.circle, size: 10, color: aviso.lido ? Colors.transparent : tema.colorScheme.primary),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(aviso.titulo, style: tema.textTheme.titleSmall?.copyWith(fontWeight: aviso.lido ? FontWeight.w500 : FontWeight.w700)),
                    const SizedBox(height: 4),
                    Text(aviso.corpo, maxLines: 2, overflow: TextOverflow.ellipsis, style: tema.textTheme.bodyMedium),
                    const SizedBox(height: 6),
                    Text(formatarDiaHora(aviso.criadoEm), style: tema.textTheme.labelSmall?.copyWith(color: tema.colorScheme.onSurfaceVariant)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
