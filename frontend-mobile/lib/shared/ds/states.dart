import 'package:flutter/material.dart';

import '../../core/network/api_error.dart';
import '../../l10n/l10n.dart';

/// Os três estados que toda tela com dados remotos precisa distinguir.
/// "Falhou" e "não há nada" são mensagens diferentes — dizer "nenhum
/// registro" quando a requisição caiu engana quem está olhando.

class LoadingView extends StatelessWidget {
  const LoadingView({super.key});

  @override
  Widget build(BuildContext context) => const Center(
    child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()),
  );
}

class ErrorView extends StatelessWidget {
  const ErrorView({super.key, required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return _Centered(
      icon: isNetworkError(error) ? Icons.wifi_off_rounded : Icons.error_outline_rounded,
      color: Theme.of(context).colorScheme.error,
      text: apiErrorMessage(error, l10n, fallback: l10n.errorLoad),
      action: OutlinedButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh_rounded), label: Text(l10n.tryAgain)),
    );
  }
}

class EmptyState extends StatelessWidget {
  const EmptyState({super.key, required this.text, this.icon = Icons.inbox_outlined});

  final String text;
  final IconData icon;

  @override
  Widget build(BuildContext context) => _Centered(icon: icon, color: Theme.of(context).colorScheme.onSurfaceVariant, text: text);
}

class _Centered extends StatelessWidget {
  const _Centered({required this.icon, required this.color, required this.text, this.action});

  final IconData icon;
  final Color color;
  final String text;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 12),
            Text(text, textAlign: TextAlign.center),
            if (action != null) ...[const SizedBox(height: 16), action!],
          ],
        ),
      ),
    );
  }
}
