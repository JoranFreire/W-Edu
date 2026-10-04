import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../router/rotas.dart';
import '../../../shared/ds/ds.dart';
import '../../../shared/rosto/rosto.dart';
import '../biometria_providers.dart';

/// Cadastro do próprio rosto: a mesma prova de vida do login (de frente e virando para os dois lados).
class CadastroFacialScreen extends ConsumerWidget {
  const CadastroFacialScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final etapa = ref.watch(cadastroFacialProvider);
    final notifier = ref.read(cadastroFacialProvider.notifier);
    final tema = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Cadastrar o rosto')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: switch (etapa) {
                  CadastroPronto() => _Aviso(Icons.face_rounded,
                      'Em um lugar bem iluminado, olhe para a câmera e vire o rosto para os dois lados quando pedir. '
                      'As fotos vão só para a conferência e não ficam no aparelho.'),
                  CadastroAbrindoCamera() || CadastroEnviando() => const Carregando(),
                  CadastroCapturando(:final passo, :final numero, :final total) =>
                    VisorDoPasso(passo: passo, numero: numero, total: total, visor: notifier.captura?.visor()),
                  CadastroFeito() => _Aviso(Icons.verified_user_rounded, 'Rosto cadastrado.'),
                  CadastroFalhou(:final mensagem) => _Aviso(Icons.error_outline_rounded, mensagem, cor: tema.colorScheme.error),
                },
              ),
              const SizedBox(height: 16),
              if (etapa is CadastroPronto || etapa is CadastroFalhou)
                FilledButton(onPressed: notifier.iniciar, child: Text(etapa is CadastroFalhou ? 'Tentar de novo' : 'Começar')),
              if (etapa is CadastroFeito)
                FilledButton(onPressed: () => context.go(Rotas.biometria), child: const Text('Concluir')),
            ],
          ),
        ),
      ),
    );
  }
}

class _Aviso extends StatelessWidget {
  const _Aviso(this.icone, this.texto, {this.cor});

  final IconData icone;
  final String texto;
  final Color? cor;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      Icon(icone, size: 72, color: cor ?? tema.colorScheme.primary),
      const SizedBox(height: 16),
      Text(texto, textAlign: TextAlign.center, style: tema.textTheme.bodyLarge?.copyWith(color: cor)),
    ]);
  }
}
