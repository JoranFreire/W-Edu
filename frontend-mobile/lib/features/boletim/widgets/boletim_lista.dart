import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/ds/ds.dart';
import '../data/boletim.dart';
import 'disciplina_card.dart';

/// Boletim (do aluno ou de um dependente), com os estados de carregamento.
class BoletimLista extends StatelessWidget {
  const BoletimLista({super.key, required this.valor, required this.onRecarregar});

  final AsyncValue<List<DisciplinaBoletim>> valor;
  final Future<void> Function() onRecarregar;

  @override
  Widget build(BuildContext context) => ListaRemota<DisciplinaBoletim>(
        valor: valor,
        onRecarregar: onRecarregar,
        textoVazio: 'Ainda não há notas publicadas.',
        iconeVazio: Icons.grading_rounded,
        itemBuilder: (context, disciplina) => DisciplinaCard(disciplina: disciplina),
      );
}
