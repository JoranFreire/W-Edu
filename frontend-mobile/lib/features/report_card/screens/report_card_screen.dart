import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/cache/watch_area.dart';
import '../../../l10n/l10n.dart';
import '../report_card_providers.dart';
import '../widgets/report_card_list.dart';

class ReportCardScreen extends ConsumerWidget {
  const ReportCardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.reportCardTitle)),
      body: ReportCardList(
        value: ref.watch(myReportCardProvider),
        onRefresh: () => ref.refreshFromApi(myReportCardProvider, ReportCardCacheKeys.mine),
      ),
    );
  }
}
