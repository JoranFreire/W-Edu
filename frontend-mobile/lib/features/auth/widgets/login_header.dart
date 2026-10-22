import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';

/// Marca e título da tela de entrada.
class LoginHeader extends StatelessWidget {
  const LoginHeader({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Icon(Icons.school_rounded, size: 48, color: theme.colorScheme.primary),
        const SizedBox(height: 16),
        Text(l10n.appTitle, textAlign: TextAlign.center, style: theme.textTheme.headlineSmall),
        const SizedBox(height: 4),
        Text(
          l10n.loginSubtitle,
          textAlign: TextAlign.center,
          style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant),
        ),
      ],
    );
  }
}
