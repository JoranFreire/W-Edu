import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/observar_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/dependente.dart';
import 'data/dependentes_repository.dart';

final dependentesRepositoryProvider = Provider<DependentesRepository>((ref) => DependentesRepository(ref.watch(dioProvider)));

abstract final class ChavesDependentes {
  static const lista = 'dependentes';
}

final dependentesProvider = StreamProvider<List<Dependente>>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesDependentes.lista,
      area: Areas.dependentes,
      baixar: ref.watch(dependentesRepositoryProvider).listar,
      ler: Dependente.lista,
    ));
