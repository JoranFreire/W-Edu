import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../router/rotas.dart';
import '../../../shared/ds/ds.dart';
import '../chamada_facial_providers.dart';
import '../widgets/fotos_da_sala.dart';
import '../widgets/revisao_chamada.dart';

/// Chamada facial de um encontro: fotos da sala → análise no Persona → revisão → confirmação.
class ChamadaScreen extends ConsumerWidget {
  const ChamadaScreen({super.key, required this.turmaId, required this.encontroId});

  final String turmaId;
  final String encontroId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chave = (turmaId: turmaId, encontroId: encontroId);
    final etapa = ref.watch(chamadaProvider(chave));
    final notifier = ref.read(chamadaProvider(chave).notifier);
    final tema = Theme.of(context);

    Future<void> avisarSeFalhou(Future<String?> acao) async {
      final mensagens = ScaffoldMessenger.of(context);
      final erro = await acao;
      if (erro != null) mensagens.showSnackBar(SnackBar(content: Text(erro)));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Chamada facial')),
      body: switch (etapa) {
        AbrindoSessao() => const _Aguarde('Abrindo a chamada…'),
        Processando() => const _Aguarde('Analisando as fotos…'),
        Confirmando() => const _Aguarde('Gravando a chamada…'),
        Fotografando() => FotosDaSala(
            etapa: etapa,
            visor: notifier.camera?.visor(),
            onFotografar: (angulo) => avisarSeFalhou(notifier.fotografar(angulo)),
            onAnalisar: notifier.analisar,
          ),
        Revisando() => RevisaoChamada(
            etapa: etapa,
            onAlternar: notifier.alternar,
            onConfirmar: () => avisarSeFalhou(notifier.confirmar()),
          ),
        ChamadaConfirmada(:final presentes, :final total) => _Final(
            icone: Icons.task_alt_rounded,
            texto: 'Chamada registrada: $presentes presente(s) de $total.',
            onVoltar: () => context.go(Rotas.chamadaTurma(turmaId)),
          ),
        ChamadaFalhou(:final mensagem) => _Final(
            icone: Icons.error_outline_rounded,
            texto: mensagem,
            cor: tema.colorScheme.error,
            onVoltar: () => context.go(Rotas.chamadaTurma(turmaId)),
          ),
      },
    );
  }
}

class _Aguarde extends StatelessWidget {
  const _Aguarde(this.texto);

  final String texto;

  @override
  Widget build(BuildContext context) => Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Carregando(),
          const SizedBox(height: 16),
          Text(texto),
        ]),
      );
}

class _Final extends StatelessWidget {
  const _Final({required this.icone, required this.texto, required this.onVoltar, this.cor});

  final IconData icone;
  final String texto;
  final VoidCallback onVoltar;
  final Color? cor;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(icone, size: 72, color: cor ?? tema.colorScheme.primary),
          const SizedBox(height: 16),
          Text(texto, textAlign: TextAlign.center, style: tema.textTheme.bodyLarge?.copyWith(color: cor)),
          const SizedBox(height: 24),
          FilledButton(onPressed: onVoltar, child: const Text('Voltar aos encontros')),
        ]),
      ),
    );
  }
}
