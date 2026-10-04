import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../benefits_providers.dart';
import '../widgets/benefits_list.dart';

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
