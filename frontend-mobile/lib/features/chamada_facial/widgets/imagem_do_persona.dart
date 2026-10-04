import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../chamada_facial_providers.dart';

/// Bytes de uma imagem do Persona (recorte do rosto ou foto do cadastro), com o token do professor.
final imagemDoPersonaProvider = FutureProvider.autoDispose.family<Uint8List, String>(
  (ref, caminho) => ref.watch(chamadaRepositoryProvider)!.imagem(caminho),
);

class ImagemDoPersona extends ConsumerWidget {
  const ImagemDoPersona({super.key, required this.caminho, required this.legenda});

  final String? caminho;
  final String legenda;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tema = Theme.of(context);
    final caminho = this.caminho;
    final imagem = caminho == null ? null : ref.watch(imagemDoPersonaProvider(caminho));
    return Column(
      children: [
        SizedBox.square(
          dimension: 96,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: switch (imagem) {
              AsyncData(:final value) => Image.memory(
                  value,
                  fit: BoxFit.cover,
                  semanticLabel: legenda,
                  errorBuilder: (_, _, _) => const Icon(Icons.broken_image_outlined),
                ),
              AsyncLoading() => const Center(child: CircularProgressIndicator()),
              _ => ColoredBox(color: tema.colorScheme.surfaceContainerHighest, child: const Icon(Icons.image_not_supported_outlined)),
            },
          ),
        ),
        const SizedBox(height: 4),
        Text(legenda, style: tema.textTheme.labelSmall),
      ],
    );
  }
}
