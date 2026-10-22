import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../attendance_providers.dart';

/// Bytes de uma imagem do Persona (recorte do rosto ou foto do cadastro), com o token do professor.
final personaImageProvider = FutureProvider.autoDispose.family<Uint8List, String>(
  (ref, path) => ref.watch(attendanceRepositoryProvider)!.image(path),
);

class PersonaImage extends ConsumerWidget {
  const PersonaImage({super.key, required this.path, required this.caption});

  final String? path;
  final String caption;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final path = this.path;
    final image = path == null ? null : ref.watch(personaImageProvider(path));
    return Column(
      children: [
        SizedBox.square(
          dimension: 96,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: switch (image) {
              AsyncData(:final value) => Image.memory(
                value,
                fit: BoxFit.cover,
                semanticLabel: caption,
                errorBuilder: (_, _, _) => const Icon(Icons.broken_image_outlined),
              ),
              AsyncLoading() => const Center(child: CircularProgressIndicator()),
              _ => ColoredBox(color: theme.colorScheme.surfaceContainerHighest, child: const Icon(Icons.image_not_supported_outlined)),
            },
          ),
        ),
        const SizedBox(height: 4),
        Text(caption, style: theme.textTheme.labelSmall),
      ],
    );
  }
}
