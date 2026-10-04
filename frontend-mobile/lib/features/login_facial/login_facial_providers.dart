import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_error.dart';
import '../../core/network/network_providers.dart';
import '../auth/auth_providers.dart';
import '../../shared/rosto/rosto.dart';
import 'data/persona_repository.dart';

/// Nulo quando o Persona não está configurado (o app fica só com senha).
final personaRepositoryProvider = Provider<PersonaRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : PersonaRepository(dio);
});

/// Etapas da tela de login facial.
sealed class EtapaLoginFacial {
  const EtapaLoginFacial();
}

class Pronto extends EtapaLoginFacial {
  const Pronto();
}

class AbrindoCamera extends EtapaLoginFacial {
  const AbrindoCamera();
}

class Capturando extends EtapaLoginFacial {
  const Capturando(this.passo, this.numero, this.total);
  final PassoDesafio passo;
  final int numero;
  final int total;
}

class Conferindo extends EtapaLoginFacial {
  const Conferindo();
}

/// O rosto não foi aceito (ou deu erro): a senha continua sempre disponível.
class NaoEntrou extends EtapaLoginFacial {
  const NaoEntrou(this.mensagem);
  final String mensagem;
}

const _recusado = 'Não foi possível entrar com o rosto. Use a senha.';

final loginFacialProvider = NotifierProvider.autoDispose<LoginFacialNotifier, EtapaLoginFacial>(LoginFacialNotifier.new);

/// Prova de vida e login: desafio do Persona → uma foto por passo → Persona
/// confere e assina → o W-Edu troca o assertion pelo token. Qualquer recusa
/// leva à senha, sem dizer o motivo (o Persona também não diz).
class LoginFacialNotifier extends Notifier<EtapaLoginFacial> {
  CapturaDeRosto? _captura;

  @override
  EtapaLoginFacial build() {
    ref.onDispose(() => _captura?.fechar());
    return const Pronto();
  }

  /// O que a câmera vê (vazio antes de abrir).
  CapturaDeRosto? get captura => _captura;

  Future<void> iniciar() async {
    if (state is AbrindoCamera || state is Capturando || state is Conferindo) return;
    final persona = ref.read(personaRepositoryProvider);
    final conta = await ref.read(contaLembradaProvider.future);
    if (persona == null || conta == null) {
      state = const NaoEntrou('Entrar com o rosto não está disponível. Use a senha.');
      return;
    }

    state = const AbrindoCamera();
    final CapturaDeRosto captura = _captura ?? ref.read(capturaDeRostoProvider);
    _captura = captura;
    try {
      await captura.abrir();
    } on Object {
      state = const NaoEntrou('Não foi possível abrir a câmera. Confira a permissão ou use a senha.');
      return;
    }

    try {
      final desafio = await persona.desafio(conta.usuarioId);
      final fotos = await capturarPassos(
        captura: captura,
        desafio: desafio,
        pausa: ref.read(pausaEntrePassosProvider),
        aoMudarDePasso: (passo, numero, total) => state = Capturando(passo, numero, total),
        continuar: () => ref.mounted,
      );
      if (!ref.mounted || fotos.length < desafio.passos.length) return;
      state = const Conferindo();
      final assertion = await persona.verificar(
        usuarioId: conta.usuarioId, instituicaoId: conta.instituicaoId, desafioId: desafio.id, fotos: fotos,
      );
      // Deu certo: o router percebe a sessão e sai da tela sozinho.
      await ref.read(authProvider.notifier).entrarComRosto(assertion);
    } on DioException catch (erro) {
      if (ref.mounted) state = NaoEntrou(erroDeRede(erro) ? mensagemDeErro(erro) : _recusado);
    } on Object {
      if (ref.mounted) state = const NaoEntrou(_recusado);
    } finally {
      await captura.fechar();
    }
  }
}
