import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/cache/watch_area.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../../shared/ds/ds.dart';
import '../data/dependent.dart';
import '../dependents_providers.dart';
import '../widgets/dependent_card.dart';

/// Portal do responsável: os alunos vinculados à conta.
class DependentsScreen extends ConsumerWidget {
  const DependentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.dependentsTitle)),
      body: RemoteList<Dependent>(
        value: ref.watch(dependentsProvider),
        onRefresh: () => ref.refreshFromApi(dependentsProvider, DependentCacheKeys.list),
        emptyText: l10n.dependentsEmpty,
        emptyIcon: Icons.family_restroom_rounded,
        itemBuilder: (context, dependent) =>
            DependentCard(dependent: dependent, onTap: () => context.go(Routes.dependent(dependent.studentId))),
      ),
    );
  }
}
