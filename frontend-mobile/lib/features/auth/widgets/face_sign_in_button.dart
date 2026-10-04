import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/network_providers.dart';
import '../../../router/routes.dart';
import '../auth_providers.dart';

/// Atalho para o login facial da conta lembrada neste aparelho. Some quando o
/// Persona não está configurado ou ninguém entrou com senha aqui ainda.
class EntrarComRosto extends ConsumerWidget {
  const EntrarComRosto({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final conta = ref.watch(contaLembradaProvider).value;
    if (conta == null || ref.watch(personaBaseUrlProvider) == null) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => context.go(Rotas.loginFacial),
          icon: const Icon(Icons.face_rounded),
          label: Text('Entrar com o rosto como ${conta.primeiroNome}'),
        ),
        TextButton(
          onPressed: () async {
            await ref.read(contaLembradaStoreProvider).esquecer();
            ref.invalidate(contaLembradaProvider);
          },
          child: Text('Não é ${conta.primeiroNome}? Usar outra conta'),
        ),
      ],
    );
  }
}
