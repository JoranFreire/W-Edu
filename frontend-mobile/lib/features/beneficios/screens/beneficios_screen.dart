import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/observar_area.dart';
import '../beneficios_providers.dart';
import '../widgets/beneficios_lista.dart';

class BeneficiosScreen extends ConsumerWidget {
  const BeneficiosScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Benefícios')),
      body: BeneficiosLista(
        valor: ref.watch(meusBeneficiosProvider),
        onRecarregar: () => ref.atualizarDaApi(meusBeneficiosProvider, ChavesBeneficios.meus),
      ),
    );
  }
}
