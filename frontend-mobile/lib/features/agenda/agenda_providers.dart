import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/agenda_item.dart';
import 'data/agenda_repository.dart';

final agendaRepositoryProvider = Provider<AgendaRepository>((ref) => AgendaRepository(ref.watch(dioProvider)));

abstract final class AgendaCacheKeys {
  static const mine = 'agenda';
  static String ofDependent(String studentId) => 'agenda_dependent_$studentId';
}

/// Agenda de quem está logado (como aluno), com cache versionado.
final myAgendaProvider = StreamProvider<List<AgendaItem>>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: AgendaCacheKeys.mine,
    area: SyncAreas.agenda,
    download: ref.watch(agendaRepositoryProvider).mine,
    parse: AgendaItem.list,
  ),
);

/// Agenda de um dependente, pelo id do aluno.
final dependentAgendaProvider = StreamProvider.family<List<AgendaItem>, String>(
  (ref, studentId) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: AgendaCacheKeys.ofDependent(studentId),
    area: SyncAreas.agenda,
    download: () => ref.read(agendaRepositoryProvider).ofDependent(studentId),
    parse: AgendaItem.list,
  ),
);
