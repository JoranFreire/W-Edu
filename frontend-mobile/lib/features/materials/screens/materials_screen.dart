import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/material_request.dart';
import '../materials_providers.dart';
import '../widgets/material_request_card.dart';

/// Requisições de material ao almoxarifado: situação e o QR de retirada das aprovadas.
/// Pedir material continua no site (lista de materiais e turmas).
class MaterialsScreen extends ConsumerWidget {
  const MaterialsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.materialsTitle)),
      body: RemoteList<MaterialRequest>(
        value: ref.watch(myMaterialRequestsProvider),
        onRefresh: () => ref.refreshFromApi(myMaterialRequestsProvider, MaterialCacheKeys.mine),
        emptyText: l10n.materialsEmpty,
        emptyIcon: Icons.inventory_2_outlined,
        itemBuilder: (_, request) => MaterialRequestCard(request: request),
      ),
    );
  }
}
