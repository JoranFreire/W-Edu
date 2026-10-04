import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/network_providers.dart';
import '../../../l10n/l10n.dart';
import '../../../router/routes.dart';
import '../auth_providers.dart';

/// Atalho para o login facial da conta lembrada neste aparelho. Some quando o
/// Persona não está configurado ou ninguém entrou com senha aqui ainda.
class FaceSignInButton extends ConsumerWidget {
  const FaceSignInButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final account = ref.watch(rememberedAccountProvider).value;
    if (account == null || ref.watch(personaBaseUrlProvider) == null) return const SizedBox.shrink();
    final l10n = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => context.go(Routes.faceLogin),
          icon: const Icon(Icons.face_rounded),
          label: Text(l10n.faceSignInAs(account.firstName)),
        ),
        TextButton(
          onPressed: () async {
            await ref.read(rememberedAccountStoreProvider).forget();
            ref.invalidate(rememberedAccountProvider);
          },
          child: Text(l10n.notYouUseAnotherAccount(account.firstName)),
        ),
      ],
    );
  }
}
