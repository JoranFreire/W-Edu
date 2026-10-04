import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../biometrics_providers.dart';
import '../data/biometric_status.dart';
import '../data/purpose.dart';
import 'biometrics_labels.dart';
import 'terms_sheet.dart';

/// Um interruptor por finalidade. Para si: a partir dos 16 anos autoriza login e catraca, e a partir dos 18
/// também a presença; abaixo de 16 só vê (quem autoriza é o responsável). Para o dependente menor de 16:
/// o responsável autoriza login e catraca.
class ConsentsList extends ConsumerWidget {
  const ConsentsList({super.key, required this.status, this.dependentId});

  final BiometricStatus status;
  final String? dependentId;

  bool get _forDependent => dependentId != null;

  String? _blockedReason(Purpose purpose, AppLocalizations l10n) {
    if (_forDependent) return null;
    if (purpose == Purpose.attendance) return status.isAdult ? null : l10n.consentAdultsOnly;
    return status.decidesAlone ? null : l10n.consentGuardianDecides;
  }

  Future<void> _toggle(BuildContext context, WidgetRef ref, Purpose purpose, bool turnOn) async {
    final actions = ref.read(consentActionsProvider);
    final messenger = ScaffoldMessenger.of(context);
    final l10n = context.l10n;
    final label = purpose.label(l10n);
    try {
      if (turnOn) {
        final terms = await actions.terms(purpose);
        if (!context.mounted) return;
        if (!await confirmTerms(context, terms, onBehalfOf: _forDependent ? status.name : null)) return;
        await actions.grant(terms, dependentId: dependentId);
        messenger.showSnackBar(SnackBar(content: Text(l10n.consentGranted(label))));
      } else {
        if (!await confirmRevoke(context, label)) return;
        await actions.revoke(purpose, dependentId: dependentId);
        messenger.showSnackBar(SnackBar(content: Text(l10n.consentRevoked(label))));
      }
    } on Object catch (error) {
      messenger.showSnackBar(SnackBar(content: Text(personaErrorMessage(error, l10n))));
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final purposes = Purpose.values.where((p) => !_forDependent || p.guardianMayConsent);
    return Column(
      children: [
        for (final purpose in purposes)
          SwitchListTile(
            secondary: Icon(purpose.icon),
            title: Text(purpose.label(l10n)),
            subtitle: Text(_blockedReason(purpose, l10n) ?? purpose.hint(l10n)),
            value: status.consented(purpose),
            onChanged: _blockedReason(purpose, l10n) == null ? (turnOn) => _toggle(context, ref, purpose, turnOn) : null,
          ),
      ],
    );
  }
}
