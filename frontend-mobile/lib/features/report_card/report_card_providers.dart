import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/report_card.dart';
import 'data/report_card_repository.dart';

final reportCardRepositoryProvider = Provider<ReportCardRepository>((ref) => ReportCardRepository(ref.watch(dioProvider)));

abstract final class ReportCardCacheKeys {
  static const mine = 'report_card';
  static String ofDependent(String studentId) => 'report_card_dependent_$studentId';
}

final myReportCardProvider = StreamProvider<List<ReportCardSubject>>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: ReportCardCacheKeys.mine,
    area: SyncAreas.reportCard,
    download: ref.watch(reportCardRepositoryProvider).mine,
    parse: ReportCardSubject.list,
  ),
);

final dependentReportCardProvider = StreamProvider.family<List<ReportCardSubject>, String>(
  (ref, studentId) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: ReportCardCacheKeys.ofDependent(studentId),
    area: SyncAreas.reportCard,
    download: () => ref.read(reportCardRepositoryProvider).ofDependent(studentId),
    parse: ReportCardSubject.list,
  ),
);
