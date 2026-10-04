import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';
import '../../../shared/ds/ds.dart';
import '../auth_providers.dart';

/// Enquanto o app confere o token salvo. Se não conseguir conferir (sem
/// rede), fica aqui com "tentar de novo" em vez de mandar para o login: a
/// sessão pode estar perfeitamente válida.
class LoadingScreen extends ConsumerWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);

    return Scaffold(
      body: SafeArea(
        child: auth.hasError && !auth.isLoading
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ErrorView(error: auth.error!, onRetry: () => ref.invalidate(authProvider)),
                  TextButton(
                    onPressed: () => ref.read(authProvider.notifier).signOut(),
                    child: Text(context.l10n.signInWithAnotherAccount),
                  ),
                ],
              )
            : const LoadingView(),
      ),
    );
  }
}
