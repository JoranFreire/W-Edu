import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/auth_providers.dart';
import '../features/notices/notices_providers.dart';
import '../l10n/l10n.dart';
import 'routes.dart';

/// A moldura das telas logadas: a barra de abas embaixo, só com as abas dos papéis da pessoa.
class ShellScreen extends ConsumerWidget {
  const ShellScreen({super.key, required this.shell});

  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tabs = AppTab.forUser(ref.watch(currentUserProvider));
    final unread = ref.watch(unreadNoticesProvider).value ?? 0;
    final current = tabs.indexWhere((tab) => tab.index == shell.currentIndex);
    final l10n = context.l10n;

    return Scaffold(
      body: shell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: current < 0 ? 0 : current,
        // Tocar na aba em que já se está volta ao topo dela.
        onDestinationSelected: (i) {
          final branch = tabs[i].index;
          shell.goBranch(branch, initialLocation: branch == shell.currentIndex);
        },
        destinations: [
          for (final tab in tabs)
            NavigationDestination(
              icon: Badge(isLabelVisible: tab == AppTab.notices && unread > 0, label: Text('$unread'), child: Icon(tab.icon)),
              selectedIcon: Icon(tab.selectedIcon),
              label: tab.label(l10n),
            ),
        ],
      ),
    );
  }
}
