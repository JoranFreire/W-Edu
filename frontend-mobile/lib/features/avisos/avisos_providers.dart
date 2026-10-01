import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import 'data/aviso.dart';
import 'data/avisos_repository.dart';

final avisosRepositoryProvider = Provider<AvisosRepository>((ref) => AvisosRepository(ref.watch(dioProvider)));

/// Quantos avisos estão sem ler (selo da aba e o resumo do início).
final avisosNaoLidosProvider = FutureProvider<int>((ref) => ref.watch(avisosRepositoryProvider).naoLidos());

final avisosProvider = AsyncNotifierProvider<AvisosNotifier, List<Aviso>>(AvisosNotifier.new);

class AvisosNotifier extends AsyncNotifier<List<Aviso>> {
  @override
  Future<List<Aviso>> build() => ref.read(avisosRepositoryProvider).listar();

  Future<void> recarregar() async {
    ref.invalidateSelf();
    ref.invalidate(avisosNaoLidosProvider);
    await future;
  }

  /// Marca na hora (a lista não pisca) e confirma com a API.
  Future<void> marcarLido(Aviso aviso) async {
    if (aviso.lido) return;
    _trocar((itens) => [for (final item in itens) item.id == aviso.id ? item.marcadoComoLido() : item]);
    await ref.read(avisosRepositoryProvider).marcarLido(aviso.id);
    ref.invalidate(avisosNaoLidosProvider);
  }

  Future<void> marcarTodos() async {
    _trocar((itens) => [for (final item in itens) item.marcadoComoLido()]);
    await ref.read(avisosRepositoryProvider).marcarTodos();
    ref.invalidate(avisosNaoLidosProvider);
  }

  void _trocar(List<Aviso> Function(List<Aviso>) mudar) {
    final atuais = state.value;
    if (atuais != null) state = AsyncData(mudar(atuais));
  }
}
