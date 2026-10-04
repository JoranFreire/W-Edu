import 'package:flutter/material.dart';

import '../chamada_facial_providers.dart';
import '../data/resultado_chamada.dart';

/// Fotos da sala: um ângulo por vez (esquerda, centro, direita). Pelo menos uma para analisar.
class FotosDaSala extends StatelessWidget {
  const FotosDaSala({super.key, required this.etapa, required this.visor, required this.onFotografar, required this.onAnalisar});

  final Fotografando etapa;
  final Widget? visor;
  final void Function(AnguloFoto angulo) onFotografar;
  final VoidCallback onAnalisar;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final sessao = etapa.sessao;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            sessao == null
                ? 'Sem internet: as fotos ficam guardadas (cifradas) e a chamada é analisada quando a rede voltar.'
                : '${sessao.comAutorizacao} aluno(s) com reconhecimento autorizado'
                    '${sessao.semAutorizacao > 0 ? ' · ${sessao.semAutorizacao} sem (você marca na revisão)' : ''}',
            style: tema.textTheme.bodyMedium,
          ),
          const SizedBox(height: 12),
          Expanded(child: ClipRRect(borderRadius: BorderRadius.circular(16), child: visor ?? const ColoredBox(color: Colors.black))),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              for (final angulo in AnguloFoto.values)
                FilledButton.tonalIcon(
                  onPressed: etapa.enviando == null ? () => onFotografar(angulo) : null,
                  icon: etapa.enviando == angulo
                      ? const SizedBox.square(dimension: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : Icon(etapa.enviadas.contains(angulo) ? Icons.check_circle_rounded : Icons.photo_camera_rounded),
                  label: Text(angulo.nome),
                ),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: etapa.enviadas.isNotEmpty && etapa.enviando == null ? onAnalisar : null,
            child: Text(sessao == null ? 'Guardar ${etapa.enviadas.length} foto(s)' : 'Analisar ${etapa.enviadas.length} foto(s)'),
          ),
        ],
      ),
    );
  }
}
