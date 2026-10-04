import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../biometrics_providers.dart';
import 'consents_list.dart';

/// Aba do dependente: o responsável autoriza o login e a catraca do menor de 16 anos. O rosto é
/// cadastrado pelo próprio aluno, no app dele; a partir dos 16, o aluno decide sozinho.
class DependentConsents extends ConsumerWidget {
  const DependentConsents({super.key, required this.studentId});

  final String studentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(dependentBiometricStatusProvider(studentId));
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return switch (status) {
      AsyncValue(:final error?, hasValue: false) => ErrorView(
        error: error,
        onRetry: () => ref.refresh(dependentBiometricStatusProvider(studentId).future),
      ),
      AsyncValue(value: final current?) =>
        current.decidesAlone
            ? EmptyState(text: l10n.dependentDecidesAlone, icon: Icons.person_rounded)
            : ListView(
                padding: const EdgeInsets.symmetric(vertical: 16),
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Text(
                      current.faceEnrolled ? l10n.dependentFaceEnrolled(current.name) : l10n.dependentEnrollAfterConsent(current.name),
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
                  ConsentsList(status: current, dependentId: studentId),
                ],
              ),
      _ => const LoadingView(),
    };
  }
}
