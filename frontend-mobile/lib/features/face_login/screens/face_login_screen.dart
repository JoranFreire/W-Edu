import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../../auth/auth_providers.dart';
import '../face_login_providers.dart';
import '../widgets/face_login_step_view.dart';

/// Entrar com o rosto, para a conta lembrada neste aparelho. A senha fica a um toque.
class FaceLoginScreen extends ConsumerWidget {
  const FaceLoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final step = ref.watch(faceLoginProvider);
    final account = ref.watch(rememberedAccountProvider).value;
    final notifier = ref.read(faceLoginProvider.notifier);
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(account == null ? l10n.faceLoginTitle : l10n.faceLoginHello(account.firstName))),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: FaceLoginStepView(step: step, preview: notifier.camera?.preview()),
              ),
              const SizedBox(height: 16),
              if (step is FaceLoginReady || step is FaceLoginFailed)
                FilledButton.icon(
                  onPressed: notifier.start,
                  icon: const Icon(Icons.face_retouching_natural),
                  label: Text(step is FaceLoginFailed ? l10n.tryAgain : l10n.start),
                ),
              TextButton(onPressed: () => context.go(Routes.login), child: Text(l10n.signInWithPassword)),
            ],
          ),
        ),
      ),
    );
  }
}
