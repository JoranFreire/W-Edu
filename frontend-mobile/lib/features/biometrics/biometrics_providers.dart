import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/network_providers.dart';
import '../../shared/face/face.dart';
import 'data/face_enrollment_repository.dart';
import 'data/consents_repository.dart';
import 'data/purpose.dart';
import 'data/refusals.dart';
import 'data/biometric_status.dart';
import 'data/terms.dart';

/// Nulos quando o Persona não está configurado (a tela nem aparece).
final consentimentosRepositoryProvider = Provider<ConsentimentosRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : ConsentimentosRepository(dio);
});

final cadastroFacialRepositoryProvider = Provider<CadastroFacialRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : CadastroFacialRepository(dio);
});

/// Situação de quem está logado (sempre da rede: autorizar e revogar valem na hora).
final minhaSituacaoBiometricaProvider = FutureProvider.autoDispose<SituacaoBiometrica>(
  (ref) => ref.watch(consentimentosRepositoryProvider)!.minhaSituacao(),
);

final situacaoDoDependenteProvider = FutureProvider.autoDispose.family<SituacaoBiometrica, String>(
  (ref, alunoId) => ref.watch(consentimentosRepositoryProvider)!.situacaoDoDependente(alunoId),
);

/// Autorizar (depois de ler o termo) e revogar, da própria pessoa ou do dependente menor.
final consentimentosAcoesProvider = Provider<ConsentimentosAcoes>(ConsentimentosAcoes.new);

class ConsentimentosAcoes {
  ConsentimentosAcoes(this._ref);

  final Ref _ref;

  ConsentimentosRepository get _repo => _ref.read(consentimentosRepositoryProvider)!;

  Future<Termos> termos(Finalidade finalidade) => _repo.termos(finalidade);

  Future<void> autorizar(Termos termos, {String? dependenteId}) async {
    await _repo.autorizar(termos, dependenteId: dependenteId);
    _atualizar(dependenteId);
  }

  Future<void> revogar(Finalidade finalidade, {String? dependenteId}) async {
    await _repo.revogar(finalidade, dependenteId: dependenteId);
    _atualizar(dependenteId);
  }

  void _atualizar(String? dependenteId) => dependenteId == null
      ? _ref.invalidate(minhaSituacaoBiometricaProvider)
      : _ref.invalidate(situacaoDoDependenteProvider(dependenteId));
}

/// Etapas do cadastro do rosto.
sealed class EtapaCadastro {
  const EtapaCadastro();
}

class CadastroPronto extends EtapaCadastro {
  const CadastroPronto();
}

class CadastroAbrindoCamera extends EtapaCadastro {
  const CadastroAbrindoCamera();
}

class CadastroCapturando extends EtapaCadastro {
  const CadastroCapturando(this.passo, this.numero, this.total);
  final PassoDesafio passo;
  final int numero;
  final int total;
}

class CadastroEnviando extends EtapaCadastro {
  const CadastroEnviando();
}

class CadastroFeito extends EtapaCadastro {
  const CadastroFeito();
}

class CadastroFalhou extends EtapaCadastro {
  const CadastroFalhou(this.mensagem);
  final String mensagem;
}

final cadastroFacialProvider = NotifierProvider.autoDispose<CadastroFacialNotifier, EtapaCadastro>(CadastroFacialNotifier.new);

/// Cadastro do próprio rosto: desafio → uma foto por passo → Persona confere a prova de vida e
/// guarda o modelo do rosto (cifrado). As fotos ficam só em memória no aparelho.
class CadastroFacialNotifier extends Notifier<EtapaCadastro> {
  CapturaDeRosto? _captura;

  @override
  EtapaCadastro build() {
    ref.onDispose(() => _captura?.fechar());
    return const CadastroPronto();
  }

  CapturaDeRosto? get captura => _captura;

  Future<void> iniciar() async {
    if (state is CadastroAbrindoCamera || state is CadastroCapturando || state is CadastroEnviando) return;
    final repo = ref.read(cadastroFacialRepositoryProvider);
    if (repo == null) {
      state = const CadastroFalhou('O reconhecimento facial não está disponível.');
      return;
    }
    state = const CadastroAbrindoCamera();
    final CapturaDeRosto captura = _captura ?? ref.read(capturaDeRostoProvider);
    _captura = captura;
    try {
      await captura.abrir();
    } on Object {
      state = const CadastroFalhou('Não foi possível abrir a câmera. Confira a permissão do app.');
      return;
    }
    try {
      final desafio = await repo.desafio();
      final fotos = await capturarPassos(
        captura: captura,
        desafio: desafio,
        pausa: ref.read(pausaEntrePassosProvider),
        aoMudarDePasso: (passo, numero, total) => state = CadastroCapturando(passo, numero, total),
        continuar: () => ref.mounted,
      );
      if (!ref.mounted || fotos.length < desafio.passos.length) return;
      state = const CadastroEnviando();
      await repo.cadastrar(desafio.id, fotos);
      if (!ref.mounted) return;
      ref.invalidate(minhaSituacaoBiometricaProvider);
      state = const CadastroFeito();
    } on Object catch (erro) {
      if (ref.mounted) state = CadastroFalhou(mensagemDoPersona(erro, 'Não foi possível cadastrar o rosto.'));
    } finally {
      await captura.fechar();
    }
  }
}
