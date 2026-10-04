import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/dependent.dart';

class DependentCard extends StatelessWidget {
  const DependentCard({super.key, required this.dependent, required this.onTap});

  final Dependent dependent;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: theme.colorScheme.primary,
          foregroundColor: theme.colorScheme.onPrimary,
          child: Text(dependent.name.characters.first.toUpperCase()),
        ),
        title: Text(dependent.name),
        subtitle: Text(relationshipLabel(dependent.relationship, l10n)),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [if (dependent.isFinancial) AppBadge(l10n.financialBadge), const Icon(Icons.chevron_right_rounded)],
        ),
        onTap: onTap,
      ),
    );
  }
}

/// Parentesco visto pelo responsável ("Você é: mãe").
String relationshipLabel(String relationship, AppLocalizations l10n) => switch (relationship) {
  'mother' => l10n.relationshipMother,
  'father' => l10n.relationshipFather,
  'legal_guardian' => l10n.relationshipLegalGuardian,
  'grandparent' => l10n.relationshipGrandparent,
  _ => l10n.relationshipOther,
};
