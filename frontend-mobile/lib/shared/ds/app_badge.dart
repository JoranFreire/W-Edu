import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

/// O selo do web: fundo claro da cor, texto na cor cheia.
class AppBadge extends StatelessWidget {
  const AppBadge(this.text, {super.key, this.color = BadgeColor.gray});

  final String text;
  final BadgeColor color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: color.color.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(999)),
      child: Text(
        text,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(color: color.color, fontWeight: FontWeight.w600),
      ),
    );
  }
}
