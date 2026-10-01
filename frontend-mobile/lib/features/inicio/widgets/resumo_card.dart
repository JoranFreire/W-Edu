import 'package:flutter/material.dart';

/// Atalho do início: ícone, título, um número ou frase e o toque leva à aba.
class ResumoCard extends StatelessWidget {
  const ResumoCard({super.key, required this.icone, required this.titulo, required this.valor, required this.onTap});

  final IconData icone;
  final String titulo;
  final String valor;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(icone, color: tema.colorScheme.primary, size: 28),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(titulo, style: tema.textTheme.labelMedium?.copyWith(color: tema.colorScheme.onSurfaceVariant)),
                    Text(valor, style: tema.textTheme.titleMedium),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded),
            ],
          ),
        ),
      ),
    );
  }
}
