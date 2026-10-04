import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_error.dart';
import 'states.dart';

/// Lista vinda da API com os três estados (carregando, erro, vazio) e "puxar
/// para atualizar". Toda tela de lista usa esta peça, para nenhuma dizer
/// "nada aqui" quando, na verdade, a requisição falhou.
class ListaRemota<T> extends StatelessWidget {
  const ListaRemota({
    super.key,
    required this.valor,
    required this.onRecarregar,
    required this.itemBuilder,
    required this.textoVazio,
    this.iconeVazio = Icons.inbox_outlined,
    this.cabecalho,
  });

  final AsyncValue<List<T>> valor;
  final Future<void> Function() onRecarregar;
  final Widget Function(BuildContext context, T item) itemBuilder;
  final String textoVazio;
  final IconData iconeVazio;

  /// Aparece acima dos itens (filtros, resumo); some nos estados de erro e vazio.
  final Widget? cabecalho;

  @override
  Widget build(BuildContext context) {
    return switch (valor) {
      AsyncValue(:final error?, hasValue: false) => ErroView(erro: error, onTentarDeNovo: onRecarregar),
      AsyncValue(value: final itens?) => RefreshIndicator(
          onRefresh: () => _recarregar(context),
          child: itens.isEmpty
              // Rolavel mesmo vazia, para o "puxar para atualizar" funcionar.
              ? ListView(children: [SizedBox(height: 320, child: EstadoVazio(texto: textoVazio, icone: iconeVazio))])
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: itens.length + (cabecalho == null ? 0 : 1),
                  separatorBuilder: (_, _) => const SizedBox(height: 12),
                  itemBuilder: (context, indice) {
                    if (cabecalho != null && indice == 0) return cabecalho!;
                    return itemBuilder(context, itens[indice - (cabecalho == null ? 0 : 1)]);
                  },
                ),
        ),
      _ => const Carregando(),
    };
  }

  /// Com a lista na tela, uma falha ao atualizar só avisa: o que está salvo continua.
  Future<void> _recarregar(BuildContext context) async {
    final mensagens = ScaffoldMessenger.of(context);
    try {
      await onRecarregar();
    } on Object catch (erro) {
      mensagens.showSnackBar(SnackBar(content: Text(mensagemDeErro(erro, 'Não foi possível atualizar.'))));
    }
  }
}
