import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import 'data/dependente.dart';
import 'data/dependentes_repository.dart';

final dependentesRepositoryProvider = Provider<DependentesRepository>((ref) => DependentesRepository(ref.watch(dioProvider)));

final dependentesProvider = FutureProvider<List<Dependente>>((ref) => ref.watch(dependentesRepositoryProvider).listar());
