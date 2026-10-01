import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../network/network_providers.dart';
import 'cache_local.dart';
import 'sincronizador.dart';
import 'versoes_repository.dart';

/// Nos testes, troca-se por um cache em memória.
final cacheLocalProvider = Provider<CacheLocal>((ref) => CacheEmArquivo());

final sincronizadorProvider = Provider<Sincronizador>((ref) => Sincronizador(ref.watch(cacheLocalProvider)));

final versoesRepositoryProvider = Provider<VersoesRepository>((ref) => VersoesRepository(ref.watch(dioProvider)));

/// Versões das áreas para a conta [dono]. Uma consulta serve a todas as telas;
/// invalidar (ao voltar para o app, ao atualizar) faz cada tela conferir de novo.
final versoesRemotasProvider = FutureProvider.autoDispose.family<Map<String, int>, String>(
  (ref, dono) => ref.watch(versoesRepositoryProvider).atuais(),
);
