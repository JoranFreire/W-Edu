import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../router/rotas.dart';
import '../data/situacao_biometrica.dart';

/// Situação do cadastro do rosto e o atalho para cadastrar (ou refazer).
class CadastroRostoCard extends StatelessWidget {
  const CadastroRostoCard({super.key, required this.situacao});

  final SituacaoBiometrica situacao;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final texto = situacao.rostoCadastrado
        ? 'Seu rosto está cadastrado.'
        : situacao.podeCadastrarRosto
            ? 'Falta cadastrar o rosto para usar o que foi autorizado.'
            : 'Autorize pelo menos um uso abaixo para cadastrar o rosto.';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(situacao.rostoCadastrado ? Icons.verified_user_rounded : Icons.face_retouching_natural, color: tema.colorScheme.primary),
              const SizedBox(width: 12),
              Expanded(child: Text(texto, style: tema.textTheme.bodyLarge)),
            ]),
            const SizedBox(height: 12),
            FilledButton.tonal(
              onPressed: situacao.podeCadastrarRosto ? () => context.go(Rotas.cadastroFacial) : null,
              child: Text(situacao.rostoCadastrado ? 'Refazer o cadastro do rosto' : 'Cadastrar meu rosto'),
            ),
          ],
        ),
      ),
    );
  }
}
