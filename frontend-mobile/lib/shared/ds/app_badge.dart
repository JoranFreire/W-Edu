import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

/// O selo do web: fundo claro da cor, texto na cor cheia.
class AppBadge extends StatelessWidget {
  const AppBadge(this.texto, {super.key, this.cor = BadgeCor.cinza});

  final String texto;
  final BadgeCor cor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: cor.cor.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(999)),
      child: Text(
        texto,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(color: cor.cor, fontWeight: FontWeight.w600),
      ),
    );
  }
}
