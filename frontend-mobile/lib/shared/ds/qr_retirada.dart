import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

/// QR de retirada em tela cheia (benefício, material do almoxarifado): fundo
/// branco (leitura fácil mesmo no tema escuro) e o código embaixo, para digitar
/// se a câmera de quem atende falhar.
class QrRetirada extends StatelessWidget {
  const QrRetirada({
    super.key,
    required this.icone,
    required this.titulo,
    required this.subtitulo,
    required this.conteudo,
    required this.codigo,
    required this.rodape,
  });

  final IconData icone;
  final String titulo;
  final String subtitulo;
  final String conteudo;
  final String codigo;
  final String rodape;

  Future<void> abrir(BuildContext context) => showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        showDragHandle: true,
        builder: (_) => SafeArea(child: this),
      );

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
      child: Column(
        children: [
          Icon(icone, size: 32, color: tema.colorScheme.primary),
          const SizedBox(height: 4),
          Text(titulo, style: tema.textTheme.titleLarge, textAlign: TextAlign.center),
          if (subtitulo.isNotEmpty) Text(subtitulo, style: tema.textTheme.bodyMedium, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
            child: QrImageView(data: conteudo, size: 260, backgroundColor: Colors.white, semanticsLabel: 'QR de $titulo'),
          ),
          const SizedBox(height: 12),
          SelectableText(codigo, style: tema.textTheme.titleMedium?.copyWith(fontFamily: 'monospace', letterSpacing: 2)),
          const SizedBox(height: 8),
          Text(rodape, style: tema.textTheme.bodySmall, textAlign: TextAlign.center),
        ],
      ),
    );
  }
}
