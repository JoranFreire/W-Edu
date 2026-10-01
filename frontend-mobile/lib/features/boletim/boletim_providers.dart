import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import 'data/boletim.dart';
import 'data/boletim_repository.dart';

final boletimRepositoryProvider = Provider<BoletimRepository>((ref) => BoletimRepository(ref.watch(dioProvider)));

final meuBoletimProvider = FutureProvider<List<DisciplinaBoletim>>((ref) => ref.watch(boletimRepositoryProvider).meu());

final boletimDoDependenteProvider = FutureProvider.family<List<DisciplinaBoletim>, String>(
  (ref, alunoId) => ref.watch(boletimRepositoryProvider).doDependente(alunoId),
);
