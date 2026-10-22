import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/cache_providers.dart';
import '../../core/network/network_providers.dart';
import '../../shared/vault/vault_providers.dart';
import 'data/auth_repository.dart';
import 'data/remembered_account.dart';
import 'data/user.dart';

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) =>
      AuthRepository(ref.watch(dioProvider), ref.watch(tokenStoreProvider), ref.watch(localCacheProvider), ref.watch(fileVaultProvider)),
);

final rememberedAccountStoreProvider = Provider<RememberedAccountStore>((ref) => SecureRememberedAccountStore());

/// A conta que pode entrar com o rosto neste aparelho (nula: só senha).
final rememberedAccountProvider = FutureProvider<RememberedAccount?>((ref) => ref.watch(rememberedAccountStoreProvider).read());

/// Quem está logado. `null` é "ninguém"; carregando é "ainda não sei" (o app
/// acabou de abrir e está conferindo o token salvo); erro é "não consegui
/// conferir" — sem rede, por exemplo, e aí a pessoa não deve ser jogada no
/// login só porque o servidor não respondeu.
final authProvider = AsyncNotifierProvider<AuthNotifier, User?>(AuthNotifier.new);

class AuthNotifier extends AsyncNotifier<User?> {
  @override
  Future<User?> build() async {
    final repo = ref.read(authRepositoryProvider);
    // A API recusou o token em alguma requisição: a sessão acabou (e o cache dela).
    ref.listen(sessionExpiredProvider, (_, _) {
      repo.signOut();
      state = const AsyncData(null);
    });

    if (!await repo.hasSession()) return null;

    // Com a sessão salva, abre na hora (inclusive offline) e confere em segundo plano.
    final saved = await repo.savedSession();
    if (saved != null) {
      _revalidate(repo);
      return saved;
    }

    try {
      return await repo.me();
    } on DioException catch (e) {
      if (e.response?.statusCode != 401) rethrow;
      await repo.signOut();
      return null;
    }
  }

  /// Atualiza nome, papéis e instituição. Sem rede, fica com a salva; token
  /// recusado cai no aviso de sessão expirada (acima).
  Future<void> _revalidate(AuthRepository repo) async {
    try {
      final user = await repo.me();
      if (ref.mounted) state = AsyncData(user);
    } on Object {
      // Mantém a sessão salva.
    }
  }

  /// Lança o erro da API em caso de falha — a tela de login mostra o motivo.
  Future<void> signIn(String email, String password) => _signedIn(ref.read(authRepositoryProvider).signIn(email, password));

  /// Com o assertion do Persona (rosto conferido); falha igual ao login com senha.
  Future<void> signInWithFace(String assertion) => _signedIn(ref.read(authRepositoryProvider).signInWithFace(assertion));

  /// Lembra a conta para o próximo login facial.
  Future<void> _signedIn(Future<User> signIn) async {
    final user = await signIn;
    await ref.read(rememberedAccountStoreProvider).save(RememberedAccount.of(user));
    ref.invalidate(rememberedAccountProvider);
    state = AsyncData(user);
  }

  Future<void> signOut() async {
    await ref.read(authRepositoryProvider).signOut();
    state = const AsyncData(null);
  }
}

/// Dono do cache das telas: cada conta (e instituição) tem o seu.
final cacheOwnerProvider = Provider<String>((ref) => ref.watch(currentUserProvider.select((user) => user.cacheOwner)));

/// Atalho para as telas que só existem com alguém logado.
final currentUserProvider = NotifierProvider<CurrentUser, User>(CurrentUser.new);

class CurrentUser extends Notifier<User> {
  @override
  User build() {
    // Ao sair, as telas logadas ainda desenham um frame antes de o router
    // tirá-las da tela. Nesse frame elas veem o último usuário, não um erro.
    final user = ref.watch(authProvider).value ?? stateOrNull;
    if (user == null) throw StateError('Authenticated screen without a signed-in user.');
    return user;
  }
}
