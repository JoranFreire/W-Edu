import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../l10n/l10n.dart';

/// QR de retirada em tela cheia (benefício, material do almoxarifado): fundo
/// branco (leitura fácil mesmo no tema escuro) e o código embaixo, para digitar
/// se a câmera de quem atende falhar.
class PickupQr extends StatelessWidget {
  const PickupQr({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.payload,
    required this.code,
    required this.footer,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final String payload;
  final String code;
  final String footer;

  Future<void> open(BuildContext context) => showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    builder: (_) => SafeArea(child: this),
  );

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
      child: Column(
        children: [
          Icon(icon, size: 32, color: theme.colorScheme.primary),
          const SizedBox(height: 4),
          Text(title, style: theme.textTheme.titleLarge, textAlign: TextAlign.center),
          if (subtitle.isNotEmpty) Text(subtitle, style: theme.textTheme.bodyMedium, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
            child: QrImageView(
              data: payload,
              size: 260,
              backgroundColor: Colors.white,
              semanticsLabel: context.l10n.qrSemanticLabel(title),
            ),
          ),
          const SizedBox(height: 12),
          SelectableText(code, style: theme.textTheme.titleMedium?.copyWith(fontFamily: 'monospace', letterSpacing: 2)),
          const SizedBox(height: 8),
          Text(footer, style: theme.textTheme.bodySmall, textAlign: TextAlign.center),
        ],
      ),
    );
  }
}
