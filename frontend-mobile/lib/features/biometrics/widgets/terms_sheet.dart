import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';
import '../data/terms.dart';
import 'biometrics_labels.dart';

/// Mostra o termo vigente; verdadeiro só se a pessoa tocar em "Li e concordo".
Future<bool> confirmTerms(BuildContext context, ConsentTerms terms, {String? onBehalfOf}) async {
  final accepted = await showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    builder: (sheetContext) {
      final theme = Theme.of(sheetContext);
      final l10n = sheetContext.l10n;
      return SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(sheetContext).height * 0.85),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 0, 24, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(terms.purpose.label(l10n), style: theme.textTheme.titleLarge),
                if (onBehalfOf != null) Text(l10n.termsOnBehalfOf(onBehalfOf), style: theme.textTheme.bodySmall),
                Text(l10n.termsVersion(terms.version), style: theme.textTheme.bodySmall),
                const SizedBox(height: 12),
                Flexible(
                  child: SingleChildScrollView(child: SelectableText(terms.text, style: theme.textTheme.bodyMedium)),
                ),
                const SizedBox(height: 16),
                FilledButton(onPressed: () => Navigator.pop(sheetContext, true), child: Text(l10n.termsAgree)),
                TextButton(onPressed: () => Navigator.pop(sheetContext, false), child: Text(l10n.notNow)),
              ],
            ),
          ),
        ),
      );
    },
  );
  return accepted ?? false;
}

/// Confirmação de revogar: o uso para na hora; sem nenhum uso ativo, o cadastro do rosto é apagado.
Future<bool> confirmRevoke(BuildContext context, String purpose) async {
  final l10n = context.l10n;
  final revoke = await showDialog<bool>(
    context: context,
    builder: (dialogContext) => AlertDialog(
      title: Text(l10n.revokeTitle(purpose)),
      content: Text(l10n.revokeBody),
      actions: [
        TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: Text(l10n.keep)),
        FilledButton(onPressed: () => Navigator.pop(dialogContext, true), child: Text(l10n.revoke)),
      ],
    ),
  );
  return revoke ?? false;
}
