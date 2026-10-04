import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/benefit.dart';
import 'data/benefits_repository.dart';

final benefitsRepositoryProvider = Provider<BenefitsRepository>((ref) => BenefitsRepository(ref.watch(dioProvider)));

abstract final class BenefitCacheKeys {
  static const mine = 'benefits';
  static String ofDependent(String studentId) => 'benefits_dependent_$studentId';
}

/// Benefícios do aluno logado, em cache: o QR abre mesmo sem rede (na fila do lanche, na entrega do kit...).
final myBenefitsProvider = StreamProvider<List<Benefit>>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: BenefitCacheKeys.mine,
    area: SyncAreas.benefits,
    download: ref.watch(benefitsRepositoryProvider).mine,
    parse: Benefit.list,
  ),
);

/// Benefícios de um dependente: o responsável mostra o QR (crianças sem celular).
final dependentBenefitsProvider = StreamProvider.family<List<Benefit>, String>(
  (ref, studentId) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: BenefitCacheKeys.ofDependent(studentId),
    area: SyncAreas.benefits,
    download: () => ref.read(benefitsRepositoryProvider).ofDependent(studentId),
    parse: Benefit.list,
  ),
);
