import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/core/cache/cache_providers.dart';
import 'package:wedu_mobile/core/network/network_providers.dart';
import 'package:wedu_mobile/features/auth/auth_providers.dart';
import 'package:wedu_mobile/shared/face/face_providers.dart';
import 'package:wedu_mobile/shared/vault/vault_providers.dart';

import 'app_harness.dart';
import 'fakes.dart';

/// Aluna (adulta por padrão) com uma dependente, os termos de login e catraca e o status de
/// consentimento que os testes mudam (`active`, `isAdult`, `decidesAlone`, `enrolled`).
class BiometricsHarness {
  BiometricsHarness() {
    _registerWEdu();
    _registerPersona();
  }

  final server = FakeServer();
  final tokens = InMemoryTokenStore('t-1');
  final camera = FakeCamera();
  List<String> active = [];
  bool isAdult = true;
  bool decidesAlone = true;
  bool enrolled = false;

  Map<String, dynamic> status() => {
    'person_name': 'Ana Souza',
    'is_adult': isAdult,
    'decides_alone': decidesAlone,
    'active_purposes': active,
    'enrollment_status': enrolled ? 'active' : 'none',
  };

  void _registerWEdu() => server
    ..on('GET users/me', (_) => (200, userJson()))
    ..on('GET institutions/current', (_) => (200, institutionJson()))
    ..on('GET access/me', (_) => (200, accessJson()))
    ..on('GET sync/versions', (_) => (200, versionsJson()))
    ..on('GET notifications/me/summary', (_) => (200, {'unread': 0, 'total': 0}))
    ..on('GET school/my/agenda', (_) => (200, <Object>[]))
    ..on('GET social/my/vouchers', (_) => (200, <Object>[]))
    ..on('GET guardians/me/dependents', (_) => (200, [dependentJson()]));

  void _registerPersona() => server
    ..on('GET consent/me/status', (req) => (req.headers['Authorization'] == 'Bearer t-1' ? 200 : 401, status()))
    ..on('GET consent/terms/LOGIN', (_) => (200, {'purpose': 'LOGIN', 'version': 'v0', 'text': 'Termo do login facial.', 'hash': 'h0'}))
    ..on('GET consent/terms/ACCESS', (_) => (200, {'purpose': 'ACCESS', 'version': 'v0', 'text': 'Termo da catraca.', 'hash': 'h1'}));

  Future<void> openApp(WidgetTester tester, {String? persona = 'http://persona/api/v1/', String role = 'student'}) async {
    server.on('GET users/me', (_) => (200, userJson(role: role)));
    await pumpWEduApp(tester, [
      tokenStoreProvider.overrideWithValue(tokens),
      httpAdapterProvider.overrideWithValue(server),
      fileVaultProvider.overrideWithValue(InMemoryVault()),
      localCacheProvider.overrideWithValue(InMemoryCache()),
      rememberedAccountStoreProvider.overrideWithValue(InMemoryRememberedAccountStore()),
      personaBaseUrlProvider.overrideWithValue(persona),
      faceCameraProvider.overrideWithValue(camera),
      stepPauseProvider.overrideWithValue(Duration.zero),
    ]);
  }

  Future<void> openBiometrics(WidgetTester tester) async {
    await tester.tap(find.descendant(of: find.byType(NavigationBar), matching: find.text('Perfil')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Reconhecimento facial'));
    await tester.pumpAndSettle();
  }
}
