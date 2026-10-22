import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/l10n.dart';

/// Texto de um resumo do início conforme o estado do dado: o valor, "toque para ver" se falhou, reticências carregando.
String summaryText<T>(AsyncValue<T> value, AppLocalizations l10n, String Function(T data) text) => switch (value) {
      AsyncData(:final value) => text(value),
      AsyncError() => l10n.homeTapToSee,
      _ => '…',
    };

String toPickUpText(int count, AppLocalizations l10n) => count == 0 ? l10n.homeNothingToPickUp : l10n.homeToPickUp(count);
