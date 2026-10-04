import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/auth_providers.dart';
import '../features/notices/notices_providers.dart';
import 'routes.dart';

/// A moldura das telas logadas: a barra de abas embaixo, só com as abas dos papéis da pessoa.
class ShellScreen extends ConsumerWidget {
  const ShellScreen({super.key, required this.shell});

  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final abas = Aba.doUsuario(ref.watch(usuarioProvider));
    final naoLidos = ref.watch(avisosNaoLidosProvider).value ?? 0;
    final atual = abas.indexWhere((aba) => aba.index == shell.currentIndex);

    return Scaffold(
      body: shell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: atual < 0 ? 0 : atual,
        // Tocar na aba em que já se está volta ao topo dela.
        onDestinationSelected: (i) {
          final ramo = abas[i].index;
          shell.goBranch(ramo, initialLocation: ramo == shell.currentIndex);
        },
        destinations: [
          for (final aba in abas)
            NavigationDestination(
              icon: Badge(isLabelVisible: aba == Aba.avisos && naoLidos > 0, label: Text('$naoLidos'), child: Icon(aba.icone)),
              selectedIcon: Icon(aba.iconeSelecionado),
              label: aba.nome,
            ),
        ],
      ),
    );
  }
}
