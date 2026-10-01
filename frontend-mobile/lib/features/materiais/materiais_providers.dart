import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/observar_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/materiais_repository.dart';
import 'data/requisicao.dart';

final materiaisRepositoryProvider = Provider<MateriaisRepository>((ref) => MateriaisRepository(ref.watch(dioProvider)));

abstract final class ChavesMateriais {
  static const minhas = 'requisicoes';
}

/// Requisições de quem pede material, em cache: o QR de retirada abre mesmo sem rede no almoxarifado.
final minhasRequisicoesProvider = StreamProvider<List<Requisicao>>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesMateriais.minhas,
      area: Areas.materiais,
      baixar: ref.watch(materiaisRepositoryProvider).minhas,
      ler: Requisicao.lista,
    ));
