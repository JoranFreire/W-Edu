import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../biometria_providers.dart';
import '../data/finalidade.dart';
import '../data/recusas.dart';
import '../data/situacao_biometrica.dart';
import 'termos_sheet.dart';

/// Um interruptor por finalidade. Para si: a partir dos 16 anos autoriza login e catraca, e a partir dos 18
/// também a presença; abaixo de 16 só vê (quem autoriza é o responsável). Para o dependente menor de 16:
/// o responsável autoriza login e catraca.
class AutorizacoesLista extends ConsumerWidget {
  const AutorizacoesLista({super.key, required this.situacao, this.dependenteId});

  final SituacaoBiometrica situacao;
  final String? dependenteId;

  bool get _doDependente => dependenteId != null;

  String? _bloqueio(Finalidade finalidade) {
    if (_doDependente) return null;
    if (finalidade == Finalidade.presenca) return situacao.ehAdulto ? null : 'Só para maiores de 18 anos.';
    return situacao.decideSozinho ? null : 'Até os 16 anos, quem autoriza é o seu responsável, pelo app dele.';
  }

  Future<void> _alternar(BuildContext context, WidgetRef ref, Finalidade finalidade, bool ligar) async {
    final acoes = ref.read(consentimentosAcoesProvider);
    final mensagens = ScaffoldMessenger.of(context);
    try {
      if (ligar) {
        final termos = await acoes.termos(finalidade);
        if (!context.mounted) return;
        if (!await confirmarTermos(context, termos, emNomeDe: _doDependente ? situacao.nome : null)) return;
        await acoes.autorizar(termos, dependenteId: dependenteId);
        mensagens.showSnackBar(SnackBar(content: Text('${finalidade.nome}: autorizado.')));
      } else {
        if (!await confirmarRevogacao(context, finalidade.nome)) return;
        await acoes.revogar(finalidade, dependenteId: dependenteId);
        mensagens.showSnackBar(SnackBar(content: Text('${finalidade.nome}: revogado.')));
      }
    } on Object catch (erro) {
      mensagens.showSnackBar(SnackBar(content: Text(mensagemDoPersona(erro, 'Não foi possível concluir.'))));
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final finalidades = Finalidade.values.where((f) => !_doDependente || f.responsavelAutoriza);
    return Column(
      children: [
        for (final finalidade in finalidades)
          SwitchListTile(
            secondary: Icon(finalidade.icone),
            title: Text(finalidade.nome),
            subtitle: Text(_bloqueio(finalidade) ?? finalidade.descricao),
            value: situacao.autorizou(finalidade),
            onChanged: _bloqueio(finalidade) == null ? (ligar) => _alternar(context, ref, finalidade, ligar) : null,
          ),
      ],
    );
  }
}
