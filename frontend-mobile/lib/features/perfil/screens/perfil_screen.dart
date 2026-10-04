import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/network_providers.dart';
import '../../../router/rotas.dart';

import '../../../shared/ds/ds.dart';
import '../../auth/auth_providers.dart';
import '../../auth/data/usuario.dart';

class PerfilScreen extends ConsumerWidget {
  const PerfilScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usuario = ref.watch(usuarioProvider);
    final papeis = usuario.papeis.map((papel) => nomesDosPapeis[papel] ?? papel).join(', ');

    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          SecaoDetalhe(
            titulo: usuario.nome,
            children: [
              LinhaDetalhe('E-mail', usuario.email),
              LinhaDetalhe(usuario.papeis.length > 1 ? 'Papéis' : 'Papel', papeis),
              LinhaDetalhe('Instituição', usuario.instituicao.nome),
            ],
          ),
          if (ref.watch(personaBaseUrlProvider) != null) ...[
            const SizedBox(height: 16),
            Card(
              child: ListTile(
                leading: const Icon(Icons.face_retouching_natural),
                title: const Text('Reconhecimento facial'),
                subtitle: const Text('Entrar com o rosto, catraca e presença: autorizações e cadastro do rosto'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go(Rotas.biometria),
              ),
            ),
          ],
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: () => _confirmarSaida(context, ref),
            icon: const Icon(Icons.logout_rounded),
            label: const Text('Sair'),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmarSaida(BuildContext context, WidgetRef ref) async {
    final confirmou = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sair da conta?'),
        content: const Text('Você vai precisar entrar de novo com e-mail e senha.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Sair')),
        ],
      ),
    );
    if (confirmou == true) await ref.read(authProvider.notifier).sair();
  }
}
