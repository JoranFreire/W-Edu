import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cache_providers.dart';

/// Tela com cache versionado: entrega o salvo e confere a versão da [area].
/// [dono] vem da sessão (cada conta tem o seu cache).
Stream<T> observarArea<T>(
  Ref ref, {
  required String dono,
  required String chave,
  required String area,
  required Future<Object?> Function() baixar,
  required T Function(Object? json) ler,
}) {
  return ref.watch(sincronizadorProvider).observar(
        dono: dono,
        chave: chave,
        area: area,
        versoes: ref.watch(versoesRemotasProvider(dono).future),
        baixar: baixar,
        ler: ler,
      );
}

extension AtualizarDaApi on WidgetRef {
  /// Puxar para atualizar: ignora o cache e a versão e baixa de novo.
  Future<T> atualizarDaApi<T>(StreamProvider<T> provider, String chave) {
    read(sincronizadorProvider).forcar(chave);
    return refresh(provider.future);
  }
}
