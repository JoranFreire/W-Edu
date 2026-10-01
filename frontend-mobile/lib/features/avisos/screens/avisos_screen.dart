import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/format/datas.dart';
import '../../../shared/ds/ds.dart';
import '../avisos_providers.dart';
import '../data/aviso.dart';
import '../widgets/aviso_card.dart';

class AvisosScreen extends ConsumerWidget {
  const AvisosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final avisos = ref.watch(avisosProvider);
    final notifier = ref.read(avisosProvider.notifier);
    final temNaoLido = avisos.value?.any((aviso) => !aviso.lido) ?? false;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Avisos'),
        actions: [
          if (temNaoLido)
            TextButton(onPressed: notifier.marcarTodos, child: const Text('Marcar todos como lidos')),
        ],
      ),
      body: ListaRemota<Aviso>(
        valor: avisos,
        onRecarregar: notifier.recarregar,
        textoVazio: 'Nenhum aviso por enquanto.',
        iconeVazio: Icons.notifications_none_rounded,
        itemBuilder: (context, aviso) => AvisoCard(
          aviso: aviso,
          onTap: () {
            notifier.marcarLido(aviso);
            _abrir(context, aviso);
          },
        ),
      ),
    );
  }

  void _abrir(BuildContext context, Aviso aviso) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(aviso.titulo, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(formatarDiaHora(aviso.criadoEm), style: Theme.of(context).textTheme.labelMedium),
              const SizedBox(height: 16),
              Text(aviso.corpo, style: Theme.of(context).textTheme.bodyLarge),
            ],
          ),
        ),
      ),
    );
  }
}
