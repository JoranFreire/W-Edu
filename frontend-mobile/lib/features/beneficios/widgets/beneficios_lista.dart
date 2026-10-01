import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/ds/ds.dart';
import '../data/beneficio.dart';
import 'beneficio_card.dart';

/// Benefícios do aluno ou de um dependente: os para retirar (com QR) no topo.
class BeneficiosLista extends StatelessWidget {
  const BeneficiosLista({super.key, required this.valor, required this.onRecarregar});

  final AsyncValue<List<Beneficio>> valor;
  final Future<void> Function() onRecarregar;

  @override
  Widget build(BuildContext context) {
    return ListaRemota<Beneficio>(
      valor: valor,
      onRecarregar: onRecarregar,
      textoVazio: 'Nenhum benefício liberado.',
      iconeVazio: Icons.redeem_outlined,
      itemBuilder: (_, beneficio) => BeneficioCard(beneficio: beneficio),
    );
  }
}
