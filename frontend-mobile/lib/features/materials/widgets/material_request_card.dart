import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/ds/ds.dart';
import '../data/material_request.dart';

class RequisicaoCard extends StatelessWidget {
  const RequisicaoCard({super.key, required this.requisicao});

  final Requisicao requisicao;

  Future<void> _abrirQr(BuildContext context) => QrRetirada(
        icone: Icons.inventory_2_rounded,
        titulo: requisicao.finalidade,
        subtitulo: requisicao.linhas.map((linha) => linha.resumo).join('\n'),
        conteudo: requisicao.conteudoQr!,
        codigo: requisicao.codigoRetirada!,
        rodape: 'Mostre este QR no almoxarifado. Só você recebe este código.',
      ).abrir(context);

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final detalhes = [
      'Para ${formatarDia(requisicao.paraDia)}',
      if (requisicao.turma != null) requisicao.turma!,
      if (requisicao.devolverAte != null) 'devolver até ${formatarDia(requisicao.devolverAte!)}',
    ].join(' · ');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(spacing: 8, runSpacing: 4, children: [
              AppBadge(requisicao.situacao.nome, cor: requisicao.situacao.cor),
              if (requisicao.atrasada) const AppBadge('Devolução atrasada', cor: BadgeCor.vermelho),
            ]),
            const SizedBox(height: 8),
            Text(requisicao.finalidade, style: tema.textTheme.titleSmall),
            const SizedBox(height: 4),
            Text(detalhes, style: tema.textTheme.labelSmall?.copyWith(color: tema.colorScheme.onSurfaceVariant)),
            const SizedBox(height: 6),
            for (final linha in requisicao.linhas) Text(linha.resumo, style: tema.textTheme.bodyMedium),
            if (requisicao.observacao != null) ...[
              const SizedBox(height: 4),
              Text(requisicao.observacao!, style: tema.textTheme.bodySmall),
            ],
            if (requisicao.paraRetirar) ...[
              const SizedBox(height: 12),
              FilledButton.tonalIcon(
                onPressed: () => _abrirQr(context),
                icon: const Icon(Icons.qr_code_2_rounded),
                label: const Text('QR de retirada'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
