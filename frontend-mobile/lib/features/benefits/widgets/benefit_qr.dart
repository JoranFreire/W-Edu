import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/benefit.dart';
import 'benefit_labels.dart';

/// O QR de retirada de um benefício (item, tipo, turma e validade).
Future<void> openBenefitQr(BuildContext context, Benefit benefit) {
  final l10n = context.l10n;
  final validity = benefit.validUntil == null ? l10n.benefitNoExpiry : l10n.benefitValidUntil(formatDay(benefit.validUntil!));
  return PickupQr(
    icon: benefit.kind.icon,
    title: '${benefit.item} × ${benefit.quantity} ${benefit.unit}',
    subtitle: [benefit.kind.label(l10n), if (benefit.offeringName.isNotEmpty) benefit.offeringName].join(' · '),
    payload: benefit.qrPayload,
    code: benefit.code,
    footer: l10n.benefitQrFooter(validity),
  ).open(context);
}
