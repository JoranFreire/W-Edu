import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../network/network_providers.dart';
import 'local_cache.dart';
import 'synchronizer.dart';
import 'versions_repository.dart';

/// Nos testes, troca-se por um cache em memória.
final localCacheProvider = Provider<LocalCache>((ref) => FileCache());

final synchronizerProvider = Provider<Synchronizer>((ref) => Synchronizer(ref.watch(localCacheProvider)));

final versionsRepositoryProvider = Provider<VersionsRepository>((ref) => VersionsRepository(ref.watch(dioProvider)));

/// Versões das áreas para a conta [owner]. Uma consulta serve a todas as telas;
/// invalidar (ao voltar para o app, ao atualizar) faz cada tela conferir de novo.
final remoteVersionsProvider = FutureProvider.autoDispose.family<Map<String, int>, String>(
  (ref, owner) => ref.watch(versionsRepositoryProvider).current(),
);
