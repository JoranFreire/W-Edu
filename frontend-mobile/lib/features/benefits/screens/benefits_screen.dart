import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../l10n/l10n.dart';
import '../benefits_providers.dart';
import '../widgets/benefits_list.dart';

class BenefitsScreen extends ConsumerWidget {
  const BenefitsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.benefitsTitle)),
      body: BenefitsList(
        value: ref.watch(myBenefitsProvider),
        onRefresh: () => ref.refreshFromApi(myBenefitsProvider, BenefitCacheKeys.mine),
      ),
    );
  }
}
