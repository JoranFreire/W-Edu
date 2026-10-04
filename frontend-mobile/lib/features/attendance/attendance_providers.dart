import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../../shared/vault/vault_providers.dart';
import '../auth/auth_providers.dart';
import 'data/attendance_queue.dart';
import 'data/attendance_repository.dart';
import 'data/attendance_uploader.dart';
import 'data/pending_attendance.dart';
import 'data/teaching.dart';
import 'data/teaching_repository.dart';

final teachingRepositoryProvider = Provider<TeachingRepository>((ref) => TeachingRepository(ref.watch(dioProvider)));

/// Nulo quando o Persona não está configurado.
final attendanceRepositoryProvider = Provider<AttendanceRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : AttendanceRepository(dio);
});

abstract final class TeachingCacheKeys {
  static const offerings = 'teaching_offerings';
  static String meetings(String offeringId) => 'teaching_meetings_$offeringId';
}

/// Turmas e encontros em cache: sem rede, o professor ainda escolhe o encontro e fotografa a sala.
final teachingOfferingsProvider = StreamProvider<List<TeachingOffering>>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: TeachingCacheKeys.offerings,
    area: SyncAreas.teaching,
    download: ref.watch(teachingRepositoryProvider).offerings,
    parse: TeachingOffering.list,
  ),
);

final meetingsProvider = StreamProvider.family<List<Meeting>, String>(
  (ref, offeringId) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: TeachingCacheKeys.meetings(offeringId),
    area: SyncAreas.teaching,
    download: () => ref.read(teachingRepositoryProvider).meetings(offeringId),
    parse: Meeting.open,
  ),
);

final attendanceQueueProvider = Provider<AttendanceQueue>((ref) => AttendanceQueue(ref.watch(fileVaultProvider)));

/// Chamadas fotografadas sem rede: tenta enviar ao abrir e quando pedirem ("Enviar agora", voltar ao app).
final pendingAttendancesProvider = AsyncNotifierProvider.autoDispose<PendingAttendances, List<PendingAttendance>>(PendingAttendances.new);

class PendingAttendances extends AsyncNotifier<List<PendingAttendance>> {
  @override
  Future<List<PendingAttendance>> build() async {
    final pending = await ref.read(attendanceQueueProvider).list();
    if (pending.any((a) => !a.isUploaded)) Future.microtask(upload);
    return pending;
  }

  /// Quantas ficaram prontas para revisão.
  Future<int> upload() async {
    final persona = ref.read(attendanceRepositoryProvider);
    if (persona == null) return 0;
    final ready = await AttendanceUploader(ref.read(attendanceQueueProvider), persona).uploadPending();
    if (ref.mounted) state = AsyncData(await ref.read(attendanceQueueProvider).list());
    return ready;
  }

  Future<void> discard(String id) async {
    await ref.read(attendanceQueueProvider).remove(id);
    if (ref.mounted) state = AsyncData(await ref.read(attendanceQueueProvider).list());
  }
}
