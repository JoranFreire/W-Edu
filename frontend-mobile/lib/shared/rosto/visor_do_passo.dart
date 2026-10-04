import 'package:flutter/material.dart';

import 'desafio.dart';

/// Câmera com a orientação do passo pedido (prova de vida).
class VisorDoPasso extends StatelessWidget {
  const VisorDoPasso({super.key, required this.passo, required this.numero, required this.total, this.visor});

  final PassoDesafio passo;
  final int numero;
  final int total;
  final Widget? visor;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Column(
      children: [
        Expanded(child: ClipRRect(borderRadius: BorderRadius.circular(24), child: visor ?? const SizedBox.expand())),
        const SizedBox(height: 16),
        Text(passo.instrucao, style: tema.textTheme.titleLarge, textAlign: TextAlign.center),
        Text('Passo $numero de $total', style: tema.textTheme.bodySmall),
      ],
    );
  }
}
