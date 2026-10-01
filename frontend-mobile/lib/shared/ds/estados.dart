import 'package:flutter/material.dart';

import '../../core/network/api_error.dart';

/// Os três estados que toda tela com dados remotos precisa distinguir.
/// "Falhou" e "não há nada" são mensagens diferentes — dizer "nenhum
/// registro" quando a requisição caiu engana quem está olhando.

class Carregando extends StatelessWidget {
  const Carregando({super.key});

  @override
  Widget build(BuildContext context) =>
      const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()));
}

class ErroView extends StatelessWidget {
  const ErroView({super.key, required this.erro, required this.onTentarDeNovo});

  final Object erro;
  final VoidCallback onTentarDeNovo;

  @override
  Widget build(BuildContext context) {
    return _Centro(
      icone: erroDeRede(erro) ? Icons.wifi_off_rounded : Icons.error_outline_rounded,
      cor: Theme.of(context).colorScheme.error,
      texto: mensagemDeErro(erro, 'Não foi possível carregar.'),
      acao: OutlinedButton.icon(
        onPressed: onTentarDeNovo,
        icon: const Icon(Icons.refresh_rounded),
        label: const Text('Tentar de novo'),
      ),
    );
  }
}

class EstadoVazio extends StatelessWidget {
  const EstadoVazio({super.key, required this.texto, this.icone = Icons.inbox_outlined});

  final String texto;
  final IconData icone;

  @override
  Widget build(BuildContext context) => _Centro(
        icone: icone,
        cor: Theme.of(context).colorScheme.onSurfaceVariant,
        texto: texto,
      );
}

class _Centro extends StatelessWidget {
  const _Centro({required this.icone, required this.cor, required this.texto, this.acao});

  final IconData icone;
  final Color cor;
  final String texto;
  final Widget? acao;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icone, size: 40, color: cor),
            const SizedBox(height: 12),
            Text(texto, textAlign: TextAlign.center),
            if (acao != null) ...[const SizedBox(height: 16), acao!],
          ],
        ),
      ),
    );
  }
}
