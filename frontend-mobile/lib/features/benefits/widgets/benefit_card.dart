import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/benefit.dart';
import 'benefit_labels.dart';
import 'benefit_qr.dart';

class BenefitCard extends StatelessWidget {
  const BenefitCard({super.key, required this.benefit});

  final Benefit benefit;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final status = benefit.status();
    final when = switch (status) {
      BenefitStatus.redeemed when benefit.redeemedAt != null => l10n.benefitRedeemedOn(formatDay(benefit.redeemedAt!.toLocal())),
      BenefitStatus.released when benefit.validUntil != null => l10n.benefitPickUpBy(formatDay(benefit.validUntil!)),
      _ => l10n.benefitReleasedOn(formatDay(benefit.releasedAt.toLocal())),
    };
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: benefit.isReadyForPickup ? () => openBenefitQr(context, benefit) : null,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(benefit.kind.icon, color: theme.colorScheme.primary),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    AppBadge(status.label(l10n), color: status.color),
                    const SizedBox(height: 8),
                    Text('${benefit.item} × ${benefit.quantity}', style: theme.textTheme.titleSmall),
                    Text(benefit.kind.label(l10n), style: theme.textTheme.bodySmall),
                    const SizedBox(height: 4),
                    Text(when, style: theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
                  ],
                ),
              ),
              if (benefit.isReadyForPickup)
                FilledButton.tonalIcon(
                  onPressed: () => openBenefitQr(context, benefit),
                  icon: const Icon(Icons.qr_code_2_rounded),
                  label: Text(l10n.showQr),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
