import 'package:flutter/material.dart';

import '../data/terms.dart';

/// Mostra o termo vigente; verdadeiro só se a pessoa tocar em "Li e concordo".
Future<bool> confirmarTermos(BuildContext context, Termos termos, {String? emNomeDe}) async {
  final aceitou = await showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    builder: (contexto) {
      final tema = Theme.of(contexto);
      return SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(contexto).height * 0.85),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 0, 24, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(termos.finalidade.nome, style: tema.textTheme.titleLarge),
                if (emNomeDe != null) Text('Autorização em nome de $emNomeDe', style: tema.textTheme.bodySmall),
                Text('Termo versão ${termos.versao}', style: tema.textTheme.bodySmall),
                const SizedBox(height: 12),
                Flexible(child: SingleChildScrollView(child: SelectableText(termos.texto, style: tema.textTheme.bodyMedium))),
                const SizedBox(height: 16),
                FilledButton(onPressed: () => Navigator.pop(contexto, true), child: const Text('Li e concordo')),
                TextButton(onPressed: () => Navigator.pop(contexto, false), child: const Text('Agora não')),
              ],
            ),
          ),
        ),
      );
    },
  );
  return aceitou ?? false;
}

/// Confirmação de revogar: o uso para na hora; sem nenhum uso ativo, o cadastro do rosto é apagado.
Future<bool> confirmarRevogacao(BuildContext context, String finalidade) async {
  final revogar = await showDialog<bool>(
    context: context,
    builder: (contexto) => AlertDialog(
      title: Text('Revogar: $finalidade?'),
      content: const Text('O rosto deixa de ser usado para isso agora. Se nenhum uso continuar autorizado, '
          'o cadastro do rosto é apagado.'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(contexto, false), child: const Text('Manter')),
        FilledButton(onPressed: () => Navigator.pop(contexto, true), child: const Text('Revogar')),
      ],
    ),
  );
  return revogar ?? false;
}
