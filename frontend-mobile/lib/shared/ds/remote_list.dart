import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_error.dart';
import '../../l10n/l10n.dart';
import 'states.dart';

/// Lista vinda da API com os três estados (carregando, erro, vazio) e "puxar
/// para atualizar". Toda tela de lista usa esta peça, para nenhuma dizer
/// "nada aqui" quando, na verdade, a requisição falhou.
class RemoteList<T> extends StatelessWidget {
  const RemoteList({
    super.key,
    required this.value,
    required this.onRefresh,
    required this.itemBuilder,
    required this.emptyText,
    this.emptyIcon = Icons.inbox_outlined,
    this.header,
  });

  final AsyncValue<List<T>> value;
  final Future<void> Function() onRefresh;
  final Widget Function(BuildContext context, T item) itemBuilder;
  final String emptyText;
  final IconData emptyIcon;

  /// Aparece acima dos itens (filtros, resumo); some nos estados de erro e vazio.
  final Widget? header;

  @override
  Widget build(BuildContext context) {
    return switch (value) {
      AsyncValue(:final error?, hasValue: false) => ErrorView(error: error, onRetry: onRefresh),
      AsyncValue(value: final items?) => RefreshIndicator(
        onRefresh: () => _refresh(context),
        child: items.isEmpty
            // Rolavel mesmo vazia, para o "puxar para atualizar" funcionar.
            ? ListView(
                children: [
                  SizedBox(
                    height: 320,
                    child: EmptyState(text: emptyText, icon: emptyIcon),
                  ),
                ],
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: items.length + (header == null ? 0 : 1),
                separatorBuilder: (_, _) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  if (header != null && index == 0) return header!;
                  return itemBuilder(context, items[index - (header == null ? 0 : 1)]);
                },
              ),
      ),
      _ => const LoadingView(),
    };
  }

  /// Com a lista na tela, uma falha ao atualizar só avisa: o que está salvo continua.
  Future<void> _refresh(BuildContext context) async {
    final messenger = ScaffoldMessenger.of(context);
    final l10n = context.l10n;
    try {
      await onRefresh();
    } on Object catch (error) {
      messenger.showSnackBar(SnackBar(content: Text(apiErrorMessage(error, l10n, fallback: l10n.errorRefresh))));
    }
  }
}
