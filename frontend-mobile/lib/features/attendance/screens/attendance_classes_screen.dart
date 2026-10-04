import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../attendance_providers.dart';
import '../data/teaching.dart';
import '../widgets/pending_attendance_section.dart';

/// Chamada facial: escolha a turma (só as que você ministra).
class ChamadaTurmasScreen extends ConsumerWidget {
  const ChamadaTurmasScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Chamada facial')),
      body: ListaRemota<TurmaDocente>(
        valor: ref.watch(turmasDocenteProvider),
        onRecarregar: () => ref.atualizarDaApi(turmasDocenteProvider, ChavesDocencia.turmas),
        textoVazio: 'Nenhuma turma para você.',
        iconeVazio: Icons.groups_outlined,
        cabecalho: const ChamadasPendentesSecao(),
        itemBuilder: (context, turma) => Card(
          child: ListTile(
            leading: const Icon(Icons.groups_rounded),
            title: Text(turma.nome),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go(Rotas.chamadaTurma(turma.id)),
          ),
        ),
      ),
    );
  }
}
