import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/ds/ds.dart';
import '../biometria_providers.dart';
import 'autorizacoes_lista.dart';

/// Aba do dependente: o responsável autoriza o login e a catraca do menor. O rosto é cadastrado
/// pelo próprio aluno, no app dele; o adulto decide tudo sozinho.
class AutorizacoesDependente extends ConsumerWidget {
  const AutorizacoesDependente({super.key, required this.alunoId});

  final String alunoId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final situacao = ref.watch(situacaoDoDependenteProvider(alunoId));
    final tema = Theme.of(context);
    return switch (situacao) {
      AsyncValue(:final error?, hasValue: false) =>
        ErroView(erro: error, onTentarDeNovo: () => ref.refresh(situacaoDoDependenteProvider(alunoId).future)),
      AsyncValue(value: final atual?) => atual.ehAdulto
          ? const EstadoVazio(texto: 'Maior de idade: o próprio aluno autoriza o uso do rosto pelo app.', icone: Icons.person_rounded)
          : ListView(
              padding: const EdgeInsets.symmetric(vertical: 16),
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    atual.rostoCadastrado
                        ? 'O rosto de ${atual.nome} está cadastrado.'
                        : 'Depois de autorizar, ${atual.nome} cadastra o próprio rosto no app (Perfil → Reconhecimento facial).',
                    style: tema.textTheme.bodyMedium,
                  ),
                ),
                AutorizacoesLista(situacao: atual, dependenteId: alunoId),
              ],
            ),
      _ => const Carregando(),
    };
  }
}
