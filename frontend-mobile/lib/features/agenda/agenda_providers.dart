import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/observar_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/agenda_repository.dart';
import 'data/item_agenda.dart';

final agendaRepositoryProvider = Provider<AgendaRepository>((ref) => AgendaRepository(ref.watch(dioProvider)));

abstract final class ChavesAgenda {
  static const minha = 'agenda';
  static String doDependente(String alunoId) => 'agenda_dependente_$alunoId';
}

/// Agenda de quem está logado (como aluno), com cache versionado.
final minhaAgendaProvider = StreamProvider<List<ItemAgenda>>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesAgenda.minha,
      area: Areas.agenda,
      baixar: ref.watch(agendaRepositoryProvider).minha,
      ler: ItemAgenda.lista,
    ));

/// Agenda de um dependente, pelo id do aluno.
final agendaDoDependenteProvider = StreamProvider.family<List<ItemAgenda>, String>((ref, alunoId) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesAgenda.doDependente(alunoId),
      area: Areas.agenda,
      baixar: () => ref.read(agendaRepositoryProvider).doDependente(alunoId),
      ler: ItemAgenda.lista,
    ));
