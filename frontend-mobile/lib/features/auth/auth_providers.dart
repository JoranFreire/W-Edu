import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import 'data/auth_repository.dart';
import 'data/usuario.dart';

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(dioProvider), ref.watch(tokenStoreProvider)),
);

/// Quem está logado. `null` é "ninguém"; carregando é "ainda não sei" (o app
/// acabou de abrir e está conferindo o token salvo); erro é "não consegui
/// conferir" — sem rede, por exemplo, e aí a pessoa não deve ser jogada no
/// login só porque o servidor não respondeu.
final authProvider = AsyncNotifierProvider<AuthNotifier, Usuario?>(AuthNotifier.new);

class AuthNotifier extends AsyncNotifier<Usuario?> {
  @override
  Future<Usuario?> build() async {
    // A API recusou o token em alguma requisição: a sessão acabou.
    ref.listen(sessaoExpiradaProvider, (_, _) => state = const AsyncData(null));

    final repo = ref.read(authRepositoryProvider);
    if (!await repo.temSessao()) return null;

    try {
      return await repo.eu();
    } on DioException catch (e) {
      if (e.response?.statusCode != 401) rethrow;
      await repo.sair();
      return null;
    }
  }

  /// Lança o erro da API em caso de falha — a tela de login mostra o motivo.
  Future<void> entrar(String email, String senha) async {
    final usuario = await ref.read(authRepositoryProvider).entrar(email, senha);
    state = AsyncData(usuario);
  }

  Future<void> sair() async {
    await ref.read(authRepositoryProvider).sair();
    state = const AsyncData(null);
  }
}

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
