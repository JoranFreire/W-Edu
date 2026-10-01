import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/format/datas.dart';
import '../../../router/rotas.dart';
import '../../agenda/agenda_providers.dart';
import '../../auth/auth_providers.dart';
import '../../avisos/avisos_providers.dart';
import '../../dependentes/dependentes_providers.dart';
import '../widgets/resumo_card.dart';

/// Resumo do dia: avisos sem ler e, conforme os papéis, a próxima atividade e os dependentes.
class InicioScreen extends ConsumerWidget {
  const InicioScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usuario = ref.watch(usuarioProvider);
    final naoLidos = ref.watch(avisosNaoLidosProvider);
    final tema = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: Text(usuario.instituicao.nome)),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(avisosNaoLidosProvider);
          if (usuario.ehAluno) ref.invalidate(minhaAgendaProvider);
          if (usuario.ehResponsavel) ref.invalidate(dependentesProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('Olá, ${usuario.primeiroNome}!', style: tema.textTheme.headlineSmall),
            const SizedBox(height: 16),
            ResumoCard(
              icone: Icons.notifications_rounded,
              titulo: 'Avisos',
              valor: switch (naoLidos) {
                AsyncData(:final value) => value == 0 ? 'Tudo lido' : '$value sem ler',
                AsyncError() => 'Toque para ver',
                _ => '…',
              },
              onTap: () => context.go(Rotas.avisos),
            ),
            if (usuario.ehAluno) ...[
              const SizedBox(height: 12),
              ResumoCard(
                icone: Icons.event_note_rounded,
                titulo: 'Próximo na agenda',
                valor: switch (ref.watch(minhaAgendaProvider)) {
                  AsyncData(:final value) => _proximo(value.map((item) => (item.titulo, item.data)).toList()),
                  AsyncError() => 'Toque para ver',
                  _ => '…',
                },
                onTap: () => context.go(Rotas.agenda),
              ),
            ],
            if (usuario.ehResponsavel) ...[
              const SizedBox(height: 12),
              ResumoCard(
                icone: Icons.family_restroom_rounded,
                titulo: 'Dependentes',
                valor: switch (ref.watch(dependentesProvider)) {
                  AsyncData(:final value) => value.isEmpty ? 'Nenhum vinculado' : value.map((d) => d.primeiroNome).join(', '),
                  AsyncError() => 'Toque para ver',
                  _ => '…',
                },
                onTap: () => context.go(Rotas.dependentes),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// O primeiro item de hoje em diante.
  String _proximo(List<(String, DateTime)> itens) {
    final hoje = DateUtils.dateOnly(DateTime.now());
    final futuro = itens.where((item) => !item.$2.isBefore(hoje)).firstOrNull;
    return futuro == null ? 'Nada pela frente' : '${futuro.$1} · ${formatarDia(futuro.$2)}';
  }
}
