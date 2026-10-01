import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import 'data/agenda_repository.dart';
import 'data/item_agenda.dart';

final agendaRepositoryProvider = Provider<AgendaRepository>((ref) => AgendaRepository(ref.watch(dioProvider)));

/// Agenda de quem está logado (como aluno).
final minhaAgendaProvider = FutureProvider<List<ItemAgenda>>((ref) => ref.watch(agendaRepositoryProvider).minha());

/// Agenda de um dependente, pelo id do aluno.
final agendaDoDependenteProvider = FutureProvider.family<List<ItemAgenda>, String>(
  (ref, alunoId) => ref.watch(agendaRepositoryProvider).doDependente(alunoId),
);
