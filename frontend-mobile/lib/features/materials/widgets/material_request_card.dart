import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../core/theme/app_colors.dart';
import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../data/material_request.dart';

class MaterialRequestCard extends StatelessWidget {
  const MaterialRequestCard({super.key, required this.request});

  final MaterialRequest request;

  Future<void> _openQr(BuildContext context, AppLocalizations l10n) => PickupQr(
    icon: Icons.inventory_2_rounded,
    title: request.purpose,
    subtitle: request.lines.map((line) => lineSummary(line, l10n)).join('\n'),
    payload: request.qrPayload!,
    code: request.pickupCode!,
    footer: l10n.materialQrFooter,
  ).open(context);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final details = [
      l10n.materialNeededOn(formatDay(request.neededOn)),
      if (request.offeringName != null) request.offeringName!,
      if (request.returnDueOn != null) l10n.materialReturnBy(formatDay(request.returnDueOn!)),
    ].join(' · ');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: [
                AppBadge(request.status.label(l10n), color: request.status.color),
                if (request.overdue) AppBadge(l10n.materialReturnOverdue, color: BadgeColor.red),
              ],
            ),
            const SizedBox(height: 8),
            Text(request.purpose, style: theme.textTheme.titleSmall),
            const SizedBox(height: 4),
            Text(details, style: theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
            const SizedBox(height: 6),
            for (final line in request.lines) Text(lineSummary(line, l10n), style: theme.textTheme.bodyMedium),
            if (request.decisionNote != null) ...[const SizedBox(height: 4), Text(request.decisionNote!, style: theme.textTheme.bodySmall)],
            if (request.isReadyForPickup) ...[
              const SizedBox(height: 12),
              FilledButton.tonalIcon(
                onPressed: () => _openQr(context, l10n),
                icon: const Icon(Icons.qr_code_2_rounded),
                label: Text(l10n.pickupQr),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// "Papel A4: 2 resma", mais o que falta devolver (permanentes).
String lineSummary(MaterialRequestLine line, AppLocalizations l10n) {
  final summary = l10n.materialLine(line.material, line.currentQuantity, line.unit);
  return line.onLoan > 0 ? l10n.materialLineToReturn(summary, line.onLoan) : summary;
}

extension MaterialRequestStatusText on MaterialRequestStatus {
  String label(AppLocalizations l10n) => switch (this) {
    MaterialRequestStatus.pending => l10n.materialStatusPending,
    MaterialRequestStatus.approved => l10n.materialStatusApproved,
    MaterialRequestStatus.rejected => l10n.materialStatusRejected,
    MaterialRequestStatus.delivered => l10n.materialStatusDelivered,
    MaterialRequestStatus.closed => l10n.materialStatusClosed,
    MaterialRequestStatus.cancelled => l10n.materialStatusCancelled,
  };
}
