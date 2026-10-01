import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/observar_area.dart';
import '../boletim_providers.dart';
import '../widgets/boletim_lista.dart';

class BoletimScreen extends ConsumerWidget {
  const BoletimScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Boletim')),
      body: BoletimLista(
        valor: ref.watch(meuBoletimProvider),
        onRecarregar: () => ref.atualizarDaApi(meuBoletimProvider, ChavesBoletim.meu),
      ),
    );
  }
}
