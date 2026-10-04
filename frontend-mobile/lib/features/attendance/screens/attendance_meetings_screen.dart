import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/format/dates.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../attendance_providers.dart';
import '../data/teaching.dart';

/// Encontros ainda abertos da turma, o de hoje primeiro.
class ChamadaEncontrosScreen extends ConsumerWidget {
  const ChamadaEncontrosScreen({super.key, required this.turmaId});

  final String turmaId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Escolha o encontro')),
      body: ListaRemota<Encontro>(
        valor: ref.watch(encontrosProvider(turmaId)),
        onRecarregar: () => ref.atualizarDaApi(encontrosProvider(turmaId), ChavesDocencia.encontros(turmaId)),
        textoVazio: 'Nenhum encontro aberto nesta turma.',
        iconeVazio: Icons.event_busy_outlined,
        itemBuilder: (context, encontro) => Card(
          child: ListTile(
            leading: const Icon(Icons.event_rounded),
            title: Text(encontro.titulo),
            subtitle: Text(formatarDiaHora(encontro.inicio)),
            trailing: const Icon(Icons.photo_camera_rounded),
            onTap: () => context.go(Rotas.chamadaEncontro(turmaId, encontro.id)),
          ),
        ),
      ),
    );
  }
}
