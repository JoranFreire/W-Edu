import 'package:dio/dio.dart';
import 'package:wedu_mobile/core/cache/local_cache.dart';
import 'package:wedu_mobile/core/cache/synchronizer.dart';

import 'fakes.dart';

/// Sincronizador sobre um cache em memória, contando quantas vezes baixou da API.
class SyncHarness {
  final cache = InMemoryCache();
  late final synchronizer = Synchronizer(cache);
  int downloads = 0;

  Future<List<List<String>>> watch({
    Future<Map<String, int>>? versions,
    String owner = 'i1_u1',
    Object? serverData = const ['new'],
    bool isOffline = false,
  }) {
    return synchronizer
        .watch<List<String>>(
          owner: owner,
          key: 'agenda',
          area: 'agenda',
          versions: versions ?? Future.value({'agenda': 2}),
          download: () async {
            downloads++;
            if (isOffline) throw offline(RequestOptions(path: 'x'));
            return serverData;
          },
          parse: (json) => [for (final item in json as List<dynamic>) item as String],
        )
        .toList();
  }

  Future<void> store(int? version, List<String> data, {String owner = 'i1_u1'}) => cache.save('$owner/agenda', CacheEntry(version, data));
}
