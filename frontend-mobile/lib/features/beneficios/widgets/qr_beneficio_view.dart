import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../core/format/datas.dart';
import '../data/beneficio.dart';

/// O QR grande, em fundo branco (leitura fácil mesmo no tema escuro), com o
/// código embaixo para digitar se a câmera de quem valida falhar.
class QrBeneficioView extends StatelessWidget {
  const QrBeneficioView({super.key, required this.beneficio});

  final Beneficio beneficio;

  static Future<void> abrir(BuildContext context, Beneficio beneficio) => showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        showDragHandle: true,
        builder: (_) => SafeArea(child: QrBeneficioView(beneficio: beneficio)),
      );

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
      child: Column(
        children: [
          Icon(beneficio.tipo.icone, size: 32, color: tema.colorScheme.primary),
          const SizedBox(height: 4),
          Text('${beneficio.item} × ${beneficio.quantidade} ${beneficio.unidade}', style: tema.textTheme.titleLarge, textAlign: TextAlign.center),
          Text([beneficio.tipo.nome, if (beneficio.turma.isNotEmpty) beneficio.turma].join(' · '), style: tema.textTheme.bodyMedium),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
            child: QrImageView(
              data: beneficio.conteudoQr,
              size: 260,
              backgroundColor: Colors.white,
              semanticsLabel: 'QR do benefício ${beneficio.item}',
            ),
          ),
          const SizedBox(height: 12),
          SelectableText(beneficio.codigo, style: tema.textTheme.titleMedium?.copyWith(fontFamily: 'monospace', letterSpacing: 2)),
          const SizedBox(height: 8),
          Text(
            beneficio.validoAte == null ? 'Sem data de validade' : 'Válido até ${formatarDia(beneficio.validoAte!)}',
            style: tema.textTheme.bodySmall,
          ),
          const SizedBox(height: 4),
          Text('Mostre este QR na retirada.', style: tema.textTheme.bodySmall),
        ],
      ),
    );
  }
}
