import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../router/rotas.dart';
import '../../../shared/ds/ds.dart';
import '../data/dependente.dart';
import '../dependentes_providers.dart';
import '../widgets/dependente_card.dart';

/// Portal do responsável: os alunos vinculados à conta.
class DependentesScreen extends ConsumerWidget {
  const DependentesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Meus dependentes')),
      body: ListaRemota<Dependente>(
        valor: ref.watch(dependentesProvider),
        onRecarregar: () => ref.refresh(dependentesProvider.future),
        textoVazio: 'Nenhum aluno vinculado à sua conta. Procure a secretaria.',
        iconeVazio: Icons.family_restroom_rounded,
        itemBuilder: (context, dependente) => DependenteCard(
          dependente: dependente,
          onTap: () => context.go(Rotas.dependente(dependente.alunoId)),
        ),
      ),
    );
  }
}
