import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';

import 'app_harness.dart';
import 'fakes.dart';

/// App de ponta a ponta com a API falsa: sessão, abas por papel, cache e idioma.
class SessionHarness {
  SessionHarness() {
    server
      ..on('GET sync/versions', (_) => (200, versionsJson()))
      ..on('GET institutions/current', (_) => (200, institutionJson()))
      ..on('GET notifications/me/summary', (_) => (200, {'unread': 3, 'total': 5}))
      ..on('GET notifications/me', (_) => (200, [noticeJson('a1')]))
      ..on('GET school/my/agenda', (_) => (200, [agendaJson('ag1')]))
      ..on('GET assessment/my/report-card', (_) => (200, [reportCardJson()]))
      ..on('GET guardians/me/dependents', (_) => (200, [dependentJson()]))
      ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
      ..on('GET access/me', (_) => (200, accessJson()));
  }

  final server = FakeServer();
  final tokens = InMemoryTokenStore();
  final cache = InMemoryCache();

  Future<void> openApp(WidgetTester tester, {Locale locale = const Locale('pt', 'BR')}) async {
    await pumpWEduApp(locale: locale, tester, [
      tokenStoreProvider.overrideWithValue(tokens),
      httpAdapterProvider.overrideWithValue(server),
      fileVaultProvider.overrideWithValue(InMemoryVault()),
      localCacheProvider.overrideWithValue(cache),
      rememberedAccountStoreProvider.overrideWithValue(InMemoryRememberedAccountStore()),
    ]);
  }

  Future<void> signIn(WidgetTester tester) async {
    await tester.enterText(find.widgetWithText(TextFormField, 'E-mail'), 'ana@escola.example.com');
    await tester.enterText(find.widgetWithText(TextFormField, 'Senha'), 'segredo123');
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();
  }
}
