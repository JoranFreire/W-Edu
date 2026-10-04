import 'package:flutter/material.dart';

import '../../../shared/ds/ds.dart';
import '../data/dependent.dart';

class DependenteCard extends StatelessWidget {
  const DependenteCard({super.key, required this.dependente, required this.onTap});

  final Dependente dependente;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: tema.colorScheme.primary,
          foregroundColor: tema.colorScheme.onPrimary,
          child: Text(dependente.nome.characters.first.toUpperCase()),
        ),
        title: Text(dependente.nome),
        subtitle: Text(nomesDoParentesco[dependente.parentesco] ?? 'Responsável'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (dependente.responsavelFinanceiro) const AppBadge('Financeiro'),
            const Icon(Icons.chevron_right_rounded),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
}
