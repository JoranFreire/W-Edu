import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import 'data/benefit.dart';
import 'data/benefits_repository.dart';

final beneficiosRepositoryProvider = Provider<BeneficiosRepository>((ref) => BeneficiosRepository(ref.watch(dioProvider)));

abstract final class ChavesBeneficios {
  static const meus = 'beneficios';
  static String doDependente(String alunoId) => 'beneficios_dependente_$alunoId';
}

/// Benefícios do aluno logado, em cache: o QR abre mesmo sem rede (na fila do lanche, na entrega do kit...).
final meusBeneficiosProvider = StreamProvider<List<Beneficio>>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesBeneficios.meus,
      area: Areas.beneficios,
      baixar: ref.watch(beneficiosRepositoryProvider).meus,
      ler: Beneficio.lista,
    ));

/// Benefícios de um dependente: o responsável mostra o QR (crianças sem celular).
final beneficiosDoDependenteProvider = StreamProvider.family<List<Beneficio>, String>((ref, alunoId) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesBeneficios.doDependente(alunoId),
      area: Areas.beneficios,
      baixar: () => ref.read(beneficiosRepositoryProvider).doDependente(alunoId),
      ler: Beneficio.lista,
    ));
