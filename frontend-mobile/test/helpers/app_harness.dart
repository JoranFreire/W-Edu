import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/app.dart';
import 'package:wedu_mobile/core/config/locale_providers.dart';

/// Abre o app (em português, salvo [locale]: os testes conferem os textos da tela), sem repetir em falha.
Future<void> pumpWEduApp(WidgetTester tester, List<Override> overrides, {Locale locale = const Locale('pt', 'BR')}) async {
  await tester.pumpWidget(
    ProviderScope(retry: (_, _) => null, overrides: [appLocaleProvider.overrideWithValue(locale), ...overrides], child: const WEduApp()),
  );
  await tester.pumpAndSettle();
}
