import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/format/datas.dart';
import '../../../router/rotas.dart';
import '../../../shared/ds/ds.dart';
import '../chamada_facial_providers.dart';
import '../data/docencia.dart';

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
        onRecarregar: () => ref.refresh(encontrosProvider(turmaId).future),
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
