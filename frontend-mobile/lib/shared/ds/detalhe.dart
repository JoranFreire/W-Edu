import 'package:flutter/material.dart';

/// Peças das telas de detalhe: um cartão com título e linhas rótulo/valor.

class SecaoDetalhe extends StatelessWidget {
  const SecaoDetalhe({super.key, required this.titulo, required this.children});

  final String titulo;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(titulo, style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }
}

class LinhaDetalhe extends StatelessWidget {
  const LinhaDetalhe(this.rotulo, this.valor, {super.key, this.destaque});

  final String rotulo;
  final String? valor;
  final Color? destaque;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              rotulo,
              style: tema.textTheme.bodyMedium?.copyWith(color: tema.colorScheme.onSurfaceVariant),
            ),
          ),
          Expanded(
            child: Text(
              valor == null || valor!.isEmpty ? '—' : valor!,
              style: tema.textTheme.bodyMedium?.copyWith(color: destaque),
            ),
          ),
        ],
      ),
    );
  }
}
