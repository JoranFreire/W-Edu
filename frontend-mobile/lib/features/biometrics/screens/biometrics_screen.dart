import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../biometrics_providers.dart';
import '../widgets/consents_list.dart';
import '../widgets/face_enrollment_card.dart';

/// Reconhecimento facial da própria pessoa: o que está autorizado, o termo de cada uso e o cadastro do rosto.
/// A senha continua valendo sempre; nada aqui é obrigatório.
class BiometricsScreen extends ConsumerWidget {
  const BiometricsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(myBiometricStatusProvider);
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.biometricsTitle)),
      body: switch (status) {
        AsyncValue(:final error?, hasValue: false) => ErrorView(error: error, onRetry: () => ref.refresh(myBiometricStatusProvider.future)),
        AsyncValue(value: final current?) => RefreshIndicator(
          onRefresh: () => ref.refresh(myBiometricStatusProvider.future),
          child: ListView(
            padding: const EdgeInsets.symmetric(vertical: 16),
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: FaceEnrollmentCard(status: current),
              ),
              const SizedBox(height: 8),
              Padding(padding: const EdgeInsets.fromLTRB(16, 8, 16, 0), child: Text(l10n.biometricsIntro)),
              ConsentsList(status: current),
            ],
          ),
        ),
        _ => const LoadingView(),
      },
    );
  }
}
