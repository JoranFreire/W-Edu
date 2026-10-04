import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../core/format/dates.dart';
import '../../../router/routes.dart';
import '../../agenda/agenda_providers.dart';
import '../../auth/auth_providers.dart';
import '../../auth/data/user.dart';
import '../../notices/notices_providers.dart';
import '../../benefits/benefits_providers.dart';
import '../../../core/network/network_providers.dart';
import '../../attendance/attendance_providers.dart';
import '../../materials/materials_providers.dart';
import '../../dependents/dependents_providers.dart';
import '../widgets/summary_card.dart';

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
        onRefresh: () => _atualizar(ref, usuario),
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
              ..._beneficios(context, ref),
            ],
            if (usuario.ministraAulas && ref.watch(personaBaseUrlProvider) != null) ...[
              const SizedBox(height: 12),
              ResumoCard(
                icone: Icons.how_to_reg_rounded,
                titulo: 'Chamada facial',
                valor: _pendentes(ref.watch(chamadasPendentesProvider).value?.length ?? 0),
                onTap: () => context.go(Rotas.chamada),
              ),
            ],
            if (usuario.podeRequisitarMaterial) ...[
              const SizedBox(height: 12),
              ResumoCard(
                icone: Icons.inventory_2_rounded,
                titulo: 'Requisições de material',
                valor: switch (ref.watch(minhasRequisicoesProvider)) {
                  AsyncData(:final value) => _retirar(value.where((r) => r.paraRetirar).length),
                  AsyncError() => 'Toque para ver',
                  _ => '…',
                },
                onTap: () => context.go(Rotas.materiais),
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

  /// Puxar para atualizar: cada resumo direto da API; sem rede, fica o salvo.
  Future<void> _atualizar(WidgetRef ref, Usuario usuario) async {
    await [
      ref.atualizarDaApi(avisosNaoLidosProvider, ChavesAvisos.resumo),
      if (usuario.ehAluno) ref.atualizarDaApi(minhaAgendaProvider, ChavesAgenda.minha),
      if (usuario.ehAluno) ref.atualizarDaApi(meusBeneficiosProvider, ChavesBeneficios.meus),
      if (usuario.ehResponsavel) ref.atualizarDaApi(dependentesProvider, ChavesDependentes.lista),
      if (usuario.podeRequisitarMaterial) ref.atualizarDaApi(minhasRequisicoesProvider, ChavesMateriais.minhas),
    ].map((atualizacao) => atualizacao.then<void>((_) {}, onError: (_) {})).wait;
  }

  /// Só aparece se a instituição já liberou algum benefício ao aluno.
  List<Widget> _beneficios(BuildContext context, WidgetRef ref) {
    final beneficios = ref.watch(meusBeneficiosProvider).value ?? const [];
    if (beneficios.isEmpty) return const [];
    final paraRetirar = beneficios.where((b) => b.paraRetirar).length;
    return [
      const SizedBox(height: 12),
      ResumoCard(
        icone: Icons.redeem_rounded,
        titulo: 'Benefícios',
        valor: paraRetirar == 0 ? 'Nada para retirar' : '$paraRetirar para retirar',
        onTap: () => context.go(Rotas.beneficios),
      ),
    ];
  }

  String _pendentes(int quantidade) => quantidade == 0 ? 'Fotografe a sala e revise' : '$quantidade chamada(s) guardada(s) no aparelho';

  String _retirar(int aprovadas) => aprovadas == 0 ? 'Nada para retirar' : '$aprovadas para retirar';

  /// O primeiro item de hoje em diante.
  String _proximo(List<(String, DateTime)> itens) {
    final hoje = DateUtils.dateOnly(DateTime.now());
    final futuro = itens.where((item) => !item.$2.isBefore(hoje)).firstOrNull;
    return futuro == null ? 'Nada pela frente' : '${futuro.$1} · ${formatarDia(futuro.$2)}';
  }
}
