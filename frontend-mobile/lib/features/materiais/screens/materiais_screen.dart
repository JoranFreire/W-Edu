import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/observar_area.dart';
import '../../../shared/ds/ds.dart';
import '../data/requisicao.dart';
import '../materiais_providers.dart';
import '../widgets/requisicao_card.dart';

/// Requisições de material ao almoxarifado: situação e o QR de retirada das aprovadas.
/// Pedir material continua no site (lista de materiais e turmas).
class MateriaisScreen extends ConsumerWidget {
  const MateriaisScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Requisições de material')),
      body: ListaRemota<Requisicao>(
        valor: ref.watch(minhasRequisicoesProvider),
        onRecarregar: () => ref.atualizarDaApi(minhasRequisicoesProvider, ChavesMateriais.minhas),
        textoVazio: 'Nenhuma requisição. Peça materiais pelo site.',
        iconeVazio: Icons.inventory_2_outlined,
        itemBuilder: (_, requisicao) => RequisicaoCard(requisicao: requisicao),
      ),
    );
  }
}
