import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/material_request.dart';
import 'data/materials_repository.dart';

final materialsRepositoryProvider = Provider<MaterialsRepository>((ref) => MaterialsRepository(ref.watch(dioProvider)));

abstract final class MaterialCacheKeys {
  static const mine = 'material_requests';
}

/// Requisições de quem pede material, em cache: o QR de retirada abre mesmo sem rede no almoxarifado.
final myMaterialRequestsProvider = StreamProvider<List<MaterialRequest>>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: MaterialCacheKeys.mine,
    area: SyncAreas.materials,
    download: ref.watch(materialsRepositoryProvider).mine,
    parse: MaterialRequest.list,
  ),
);
