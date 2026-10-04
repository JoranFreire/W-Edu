import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/cache_providers.dart';
import '../../core/cache/sync_areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/notice.dart';
import 'data/notices_repository.dart';

final noticesRepositoryProvider = Provider<NoticesRepository>((ref) => NoticesRepository(ref.watch(dioProvider)));

abstract final class NoticeCacheKeys {
  static const list = 'notices';
  static const summary = 'notices_summary';
}

/// Quantos avisos estão sem ler (selo da aba e o resumo do início).
final unreadNoticesProvider = StreamProvider<int>(
  (ref) => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: NoticeCacheKeys.summary,
    area: SyncAreas.notices,
    download: ref.watch(noticesRepositoryProvider).summary,
    parse: (json) => (json as Map<String, dynamic>)['unread'] as int,
  ),
);

final noticesProvider = StreamNotifierProvider<NoticesNotifier, List<Notice>>(NoticesNotifier.new);

class NoticesNotifier extends StreamNotifier<List<Notice>> {
  @override
  Stream<List<Notice>> build() => watchArea(
    ref,
    owner: ref.watch(cacheOwnerProvider),
    key: NoticeCacheKeys.list,
    area: SyncAreas.notices,
    download: ref.watch(noticesRepositoryProvider).list,
    parse: Notice.list,
  );

  /// Puxar para atualizar: lista e contagem direto da API.
  Future<void> reload() async {
    ref.read(synchronizerProvider)
      ..force(NoticeCacheKeys.list)
      ..force(NoticeCacheKeys.summary);
    ref.invalidate(unreadNoticesProvider);
    ref.invalidateSelf();
    await future;
  }

  /// Marca na hora (a lista não pisca) e confirma com a API.
  Future<void> markAsRead(Notice notice) async {
    if (notice.isRead) return;
    await _confirm(
      (items) => [for (final item in items) item.id == notice.id ? item.markedAsRead() : item],
      () => ref.read(noticesRepositoryProvider).markAsRead(notice.id),
    );
  }

  Future<void> markAllAsRead() =>
      _confirm((items) => [for (final item in items) item.markedAsRead()], ref.read(noticesRepositoryProvider).markAllAsRead);

  Future<void> _confirm(List<Notice> Function(List<Notice>) change, Future<void> Function() callApi) async {
    final current = state.value;
    if (current == null) return;
    final updated = change(current);
    state = AsyncData(updated);
    try {
      await callApi();
    } catch (_) {
      // Não confirmou (sem rede, por exemplo): volta ao que está salvo.
      ref.invalidateSelf();
      return;
    }
    await ref.read(synchronizerProvider).rewrite(ref.read(cacheOwnerProvider), NoticeCacheKeys.list, [
      for (final notice in updated) notice.toJson(),
    ]);
    ref.read(synchronizerProvider).force(NoticeCacheKeys.summary);
    ref.invalidate(unreadNoticesProvider);
  }
}
