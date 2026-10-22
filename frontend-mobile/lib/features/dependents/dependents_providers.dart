import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/dependent.dart';
import 'data/dependents_repository.dart';

final dependentsRepositoryProvider = Provider<DependentsRepository>((ref) => DependentsRepository(ref.watch(dioProvider)));

abstract final class DependentCacheKeys {
  static const list = 'dependents';
}

final dependentsProvider = StreamProvider<List<Dependent>>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: DependentCacheKeys.list,
    area: SyncAreas.dependents,
    download: ref.watch(dependentsRepositoryProvider).list,
    parse: Dependent.list,
  ),
);
