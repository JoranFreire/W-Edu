import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/report_card.dart';
import 'data/report_card_repository.dart';

final boletimRepositoryProvider = Provider<BoletimRepository>((ref) => BoletimRepository(ref.watch(dioProvider)));

abstract final class ChavesBoletim {
  static const meu = 'boletim';
  static String doDependente(String alunoId) => 'boletim_dependente_$alunoId';
}

final meuBoletimProvider = StreamProvider<List<DisciplinaBoletim>>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesBoletim.meu,
      area: Areas.boletim,
      baixar: ref.watch(boletimRepositoryProvider).meu,
      ler: DisciplinaBoletim.lista,
    ));

final boletimDoDependenteProvider = StreamProvider.family<List<DisciplinaBoletim>, String>((ref, alunoId) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesBoletim.doDependente(alunoId),
      area: Areas.boletim,
      baixar: () => ref.read(boletimRepositoryProvider).doDependente(alunoId),
      ler: DisciplinaBoletim.lista,
    ));
