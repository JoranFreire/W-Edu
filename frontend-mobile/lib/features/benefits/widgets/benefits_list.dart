import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/benefit.dart';
import 'benefit_card.dart';

/// Benefícios do aluno ou de um dependente: os para retirar (com QR) no topo.
class BenefitsList extends StatelessWidget {
  const BenefitsList({super.key, required this.value, required this.onRefresh});

  final AsyncValue<List<Benefit>> value;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    return RemoteList<Benefit>(
      value: value,
      onRefresh: onRefresh,
      emptyText: context.l10n.benefitsEmpty,
      emptyIcon: Icons.redeem_outlined,
      itemBuilder: (_, benefit) => BenefitCard(benefit: benefit),
    );
  }
}
