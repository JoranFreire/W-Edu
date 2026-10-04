import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/cache_providers.dart';
import '../../core/network/network_providers.dart';
import '../../shared/vault/vault_providers.dart';
import 'data/auth_repository.dart';
import 'data/remembered_account.dart';
import 'data/user.dart';

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(dioProvider), ref.watch(tokenStoreProvider), ref.watch(cacheLocalProvider), ref.watch(cofreProvider)),
);

final contaLembradaStoreProvider = Provider<ContaLembradaStore>((ref) => SecureContaLembradaStore());

/// A conta que pode entrar com o rosto neste aparelho (nula: só senha).
final contaLembradaProvider = FutureProvider<ContaLembrada?>((ref) => ref.watch(contaLembradaStoreProvider).ler());

/// Quem está logado. `null` é "ninguém"; carregando é "ainda não sei" (o app
/// acabou de abrir e está conferindo o token salvo); erro é "não consegui
/// conferir" — sem rede, por exemplo, e aí a pessoa não deve ser jogada no
/// login só porque o servidor não respondeu.
final authProvider = AsyncNotifierProvider<AuthNotifier, Usuario?>(AuthNotifier.new);

class AuthNotifier extends AsyncNotifier<Usuario?> {
  @override
  Future<Usuario?> build() async {
    final repo = ref.read(authRepositoryProvider);
    // A API recusou o token em alguma requisição: a sessão acabou (e o cache dela).
    ref.listen(sessaoExpiradaProvider, (_, _) {
      repo.sair();
      state = const AsyncData(null);
    });

    if (!await repo.temSessao()) return null;

    // Com a sessão salva, abre na hora (inclusive offline) e confere em segundo plano.
    final salva = await repo.sessaoSalva();
    if (salva != null) {
      _conferir(repo);
      return salva;
    }

    try {
      return await repo.eu();
    } on DioException catch (e) {
      if (e.response?.statusCode != 401) rethrow;
      await repo.sair();
      return null;
    }
  }

  /// Atualiza nome, papéis e instituição. Sem rede, fica com a salva; token
  /// recusado cai no aviso de sessão expirada (acima).
  Future<void> _conferir(AuthRepository repo) async {
    try {
      final usuario = await repo.eu();
      if (ref.mounted) state = AsyncData(usuario);
    } on Object {
      // Mantém a sessão salva.
    }
  }

  /// Lança o erro da API em caso de falha — a tela de login mostra o motivo.
  Future<void> entrar(String email, String senha) => _entrou(ref.read(authRepositoryProvider).entrar(email, senha));

  /// Com o assertion do Persona (rosto conferido); falha igual ao login com senha.
  Future<void> entrarComRosto(String assertion) => _entrou(ref.read(authRepositoryProvider).entrarComRosto(assertion));

  /// Lembra a conta para o próximo login facial.
  Future<void> _entrou(Future<Usuario> login) async {
    final usuario = await login;
    await ref.read(contaLembradaStoreProvider).salvar(ContaLembrada.de(usuario));
    ref.invalidate(contaLembradaProvider);
    state = AsyncData(usuario);
  }

  Future<void> sair() async {
    await ref.read(authRepositoryProvider).sair();
    state = const AsyncData(null);
  }
}

/// Dono do cache das telas: cada conta (e instituição) tem o seu.
final donoDoCacheProvider = Provider<String>((ref) => ref.watch(usuarioProvider.select((usuario) => usuario.chaveDoCache)));

/// Atalho para as telas que só existem com alguém logado.
final usuarioProvider = NotifierProvider<UsuarioLogado, Usuario>(UsuarioLogado.new);

class UsuarioLogado extends Notifier<Usuario> {
  @override
  Usuario build() {
    // Ao sair, as telas logadas ainda desenham um frame antes de o router
    // tirá-las da tela. Nesse frame elas veem o último usuário, não um erro.
    final usuario = ref.watch(authProvider).value ?? stateOrNull;
    if (usuario == null) throw StateError('Tela autenticada sem ninguém logado.');
    return usuario;
  }
}
