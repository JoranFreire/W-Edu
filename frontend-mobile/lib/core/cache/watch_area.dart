import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cache_providers.dart';

/// Tela com cache versionado: entrega o salvo e confere a versão da [area].
/// [owner] vem da sessão (cada conta tem o seu cache).
Stream<T> watchArea<T>(
  Ref ref, {
  required String owner,
  required String key,
  required String area,
  required Future<Object?> Function() download,
  required T Function(Object? json) parse,
}) {
  return ref
      .watch(synchronizerProvider)
      .watch(
        owner: owner,
        key: key,
        area: area,
        versions: ref.watch(remoteVersionsProvider(owner).future),
        download: download,
        parse: parse,
      );
}

extension RefreshFromApi on WidgetRef {
  /// Puxar para atualizar: ignora o cache e a versão e baixa de novo.
  Future<T> refreshFromApi<T>(StreamProvider<T> provider, String key) {
    read(synchronizerProvider).force(key);
    return refresh(provider.future);
  }
}
