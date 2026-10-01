import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/cache_providers.dart';
import '../../core/cache/observar_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/aviso.dart';
import 'data/avisos_repository.dart';

final avisosRepositoryProvider = Provider<AvisosRepository>((ref) => AvisosRepository(ref.watch(dioProvider)));

abstract final class ChavesAvisos {
  static const lista = 'avisos';
  static const resumo = 'avisos_resumo';
}

/// Quantos avisos estão sem ler (selo da aba e o resumo do início).
final avisosNaoLidosProvider = StreamProvider<int>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesAvisos.resumo,
      area: Areas.avisos,
      baixar: ref.watch(avisosRepositoryProvider).resumo,
      ler: (json) => (json as Map<String, dynamic>)['unread'] as int,
    ));

final avisosProvider = StreamNotifierProvider<AvisosNotifier, List<Aviso>>(AvisosNotifier.new);

class AvisosNotifier extends StreamNotifier<List<Aviso>> {
  @override
  Stream<List<Aviso>> build() => observarArea(
        ref,
        dono: ref.watch(donoDoCacheProvider),
        chave: ChavesAvisos.lista,
        area: Areas.avisos,
        baixar: ref.watch(avisosRepositoryProvider).listar,
        ler: Aviso.lista,
      );

  /// Puxar para atualizar: lista e contagem direto da API.
  Future<void> recarregar() async {
    ref.read(sincronizadorProvider)
      ..forcar(ChavesAvisos.lista)
      ..forcar(ChavesAvisos.resumo);
    ref.invalidate(avisosNaoLidosProvider);
    ref.invalidateSelf();
    await future;
  }

  /// Marca na hora (a lista não pisca) e confirma com a API.
  Future<void> marcarLido(Aviso aviso) async {
    if (aviso.lido) return;
    await _confirmar(
      (itens) => [for (final item in itens) item.id == aviso.id ? item.marcadoComoLido() : item],
      () => ref.read(avisosRepositoryProvider).marcarLido(aviso.id),
    );
  }

  Future<void> marcarTodos() => _confirmar(
        (itens) => [for (final item in itens) item.marcadoComoLido()],
        ref.read(avisosRepositoryProvider).marcarTodos,
      );

  Future<void> _confirmar(List<Aviso> Function(List<Aviso>) mudar, Future<void> Function() chamarApi) async {
    final atuais = state.value;
    if (atuais == null) return;
    final novos = mudar(atuais);
    state = AsyncData(novos);
    try {
      await chamarApi();
    } catch (_) {
      // Não confirmou (sem rede, por exemplo): volta ao que está salvo.
      ref.invalidateSelf();
      return;
    }
    await ref.read(sincronizadorProvider).regravar(
          ref.read(donoDoCacheProvider),
          ChavesAvisos.lista,
          [for (final aviso in novos) aviso.toJson()],
        );
    ref.read(sincronizadorProvider).forcar(ChavesAvisos.resumo);
    ref.invalidate(avisosNaoLidosProvider);
  }
}
