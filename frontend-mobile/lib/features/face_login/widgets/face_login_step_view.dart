import 'package:flutter/material.dart';

import '../../../shared/face/face.dart';
import '../face_login_providers.dart';

/// O meio da tela: orientação, visor da câmera com o passo pedido, conferência ou recusa.
class EtapaLoginFacialView extends StatelessWidget {
  const EtapaLoginFacialView({super.key, required this.etapa, this.visor});

  final EtapaLoginFacial etapa;
  final Widget? visor;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return switch (etapa) {
      Pronto() => _Mensagem(
          icone: Icons.face_rounded,
          texto: 'Vamos conferir que é você.\nVocê vai olhar para a câmera e virar o rosto para os dois lados.',
        ),
      AbrindoCamera() || Conferindo() => Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(etapa is Conferindo ? 'Conferindo…' : 'Abrindo a câmera…', style: tema.textTheme.bodyLarge),
          ],
        ),
      Capturando(:final passo, :final numero, :final total) => VisorDoPasso(passo: passo, numero: numero, total: total, visor: visor),
      NaoEntrou(:final mensagem) => _Mensagem(icone: Icons.no_accounts_rounded, texto: mensagem, cor: tema.colorScheme.error),
    };
  }
}

class _Mensagem extends StatelessWidget {
  const _Mensagem({required this.icone, required this.texto, this.cor});

  final IconData icone;
  final String texto;
  final Color? cor;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icone, size: 72, color: cor ?? tema.colorScheme.primary),
        const SizedBox(height: 16),
        Text(texto, textAlign: TextAlign.center, style: tema.textTheme.bodyLarge?.copyWith(color: cor)),
      ],
    );
  }
}
