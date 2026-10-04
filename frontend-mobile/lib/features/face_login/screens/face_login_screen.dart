import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../router/routes.dart';
import '../../auth/auth_providers.dart';
import '../face_login_providers.dart';
import '../widgets/face_login_step_view.dart';

/// Entrar com o rosto, para a conta lembrada neste aparelho. A senha fica a um toque.
class LoginFacialScreen extends ConsumerWidget {
  const LoginFacialScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final etapa = ref.watch(loginFacialProvider);
    final conta = ref.watch(contaLembradaProvider).value;
    final notifier = ref.read(loginFacialProvider.notifier);
    return Scaffold(
      appBar: AppBar(title: Text(conta == null ? 'Entrar com o rosto' : 'Olá, ${conta.primeiroNome}')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(child: EtapaLoginFacialView(etapa: etapa, visor: notifier.captura?.visor())),
              const SizedBox(height: 16),
              if (etapa is Pronto || etapa is NaoEntrou)
                FilledButton.icon(
                  onPressed: notifier.iniciar,
                  icon: const Icon(Icons.face_retouching_natural),
                  label: Text(etapa is NaoEntrou ? 'Tentar de novo' : 'Começar'),
                ),
              TextButton(onPressed: () => context.go(Rotas.login), child: const Text('Entrar com a senha')),
            ],
          ),
        ),
      ),
    );
  }
}
