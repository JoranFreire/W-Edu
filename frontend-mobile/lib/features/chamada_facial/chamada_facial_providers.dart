import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_error.dart';
import '../../core/network/network_providers.dart';
import '../../shared/rosto/rosto.dart';
import 'data/chamada_repository.dart';
import 'data/docencia.dart';
import 'data/docencia_repository.dart';
import 'data/resultado_chamada.dart';

final docenciaRepositoryProvider = Provider<DocenciaRepository>((ref) => DocenciaRepository(ref.watch(dioProvider)));

/// Nulo quando o Persona não está configurado.
final chamadaRepositoryProvider = Provider<ChamadaRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : ChamadaRepository(dio);
});

final turmasDocenteProvider = FutureProvider.autoDispose<List<TurmaDocente>>((ref) => ref.watch(docenciaRepositoryProvider).turmas());

final encontrosProvider = FutureProvider.autoDispose.family<List<Encontro>, String>(
  (ref, turmaId) => ref.watch(docenciaRepositoryProvider).encontros(turmaId),
);

/// Intervalo entre as consultas do resultado enquanto o Persona processa as fotos (zero nos testes).
final intervaloDoResultadoProvider = Provider<Duration>((ref) => const Duration(seconds: 2));
const _maximoDeConsultas = 90;

/// Etapas da chamada de um encontro.
sealed class EtapaChamada {
  const EtapaChamada();
}

class AbrindoSessao extends EtapaChamada {
  const AbrindoSessao();
}

class Fotografando extends EtapaChamada {
  const Fotografando(this.sessao, this.enviadas, {this.enviando});
  final SessaoChamada sessao;
  final Set<AnguloFoto> enviadas;
  final AnguloFoto? enviando;
}

class Processando extends EtapaChamada {
  const Processando();
}

class Revisando extends EtapaChamada {
  const Revisando(this.sessao, this.resultado, this.presentes);
  final SessaoChamada sessao;
  final ResultadoChamada resultado;

  /// Quem será confirmado presente (começa com os reconhecidos; o professor ajusta).
  final Set<String> presentes;
}

class Confirmando extends EtapaChamada {
  const Confirmando();
}

class ChamadaConfirmada extends EtapaChamada {
  const ChamadaConfirmada(this.presentes, this.total);
  final int presentes;
  final int total;
}

class ChamadaFalhou extends EtapaChamada {
  const ChamadaFalhou(this.mensagem);
  final String mensagem;
}

typedef ChaveChamada = ({String turmaId, String encontroId});

final chamadaProvider = NotifierProvider.autoDispose.family<ChamadaNotifier, EtapaChamada, ChaveChamada>(ChamadaNotifier.new);

/// Chamada facial de um encontro. O resultado nunca vale sozinho: o professor revisa e confirma,
/// e só então o Persona grava e repassa ao W-Edu.
class ChamadaNotifier extends Notifier<EtapaChamada> {
  ChamadaNotifier(this.chave);

  final ChaveChamada chave;
  CapturaDeRosto? _camera;
  bool _cameraAberta = false;

  @override
  EtapaChamada build() {
    ref.onDispose(() => _camera?.fechar());
    Future.microtask(_abrir);
    return const AbrindoSessao();
  }

  ChamadaRepository get _repo => ref.read(chamadaRepositoryProvider)!;

  /// O visor da câmera traseira (vazio antes de abrir).
  CapturaDeRosto? get camera => _camera;

  Future<void> _abrir() async {
    try {
      final sessao = await _repo.abrir(turmaId: chave.turmaId, encontroId: chave.encontroId);
      if (!ref.mounted) return;
      final CapturaDeRosto camera = ref.read(cameraDeSalaProvider);
      _camera = camera;
      await camera.abrir();
      _cameraAberta = true;
      if (ref.mounted) state = Fotografando(sessao, const {});
    } on Object catch (erro) {
      if (ref.mounted) state = ChamadaFalhou(_mensagem(erro, 'Não foi possível abrir a chamada.'));
    }
  }

  /// Nulo se a foto foi enviada; senão, o motivo (a tela avisa e a pessoa tenta de novo).
  Future<String?> fotografar(AnguloFoto angulo) async {
    final atual = state;
    if (atual is! Fotografando || atual.enviando != null || !_cameraAberta) return null;
    state = Fotografando(atual.sessao, atual.enviadas, enviando: angulo);
    try {
      final foto = await _camera!.fotografar();
      await _repo.enviarFoto(atual.sessao.id, angulo, foto, DateTime.now());
      if (ref.mounted) state = Fotografando(atual.sessao, {...atual.enviadas, angulo});
      return null;
    } on Object catch (erro) {
      if (ref.mounted) state = Fotografando(atual.sessao, atual.enviadas);
      return _mensagem(erro, 'Não foi possível enviar a foto.');
    }
  }

  /// Espera o Persona processar todas as fotos e abre a revisão.
  Future<void> analisar() async {
    final atual = state;
    if (atual is! Fotografando || atual.enviadas.isEmpty) return;
    state = const Processando();
    await _camera?.fechar();
    _cameraAberta = false;
    try {
      for (var consulta = 0; consulta < _maximoDeConsultas; consulta++) {
        final resultado = await _repo.resultado(atual.sessao.id);
        if (!ref.mounted) return;
        if (resultado.fotosPendentes == 0) {
          final reconhecidos = resultado.de(SituacaoNaFoto.presente).map((a) => a.pessoaId).toSet();
          state = Revisando(atual.sessao, resultado, reconhecidos);
          return;
        }
        await Future<void>.delayed(ref.read(intervaloDoResultadoProvider));
      }
      state = const ChamadaFalhou('As fotos ainda estão sendo analisadas. Tente de novo em instantes.');
    } on Object catch (erro) {
      if (ref.mounted) state = ChamadaFalhou(_mensagem(erro, 'Não foi possível analisar as fotos.'));
    }
  }

  void alternar(String pessoaId) {
    final atual = state;
    if (atual is! Revisando) return;
    final presentes = {...atual.presentes};
    presentes.contains(pessoaId) ? presentes.remove(pessoaId) : presentes.add(pessoaId);
    state = Revisando(atual.sessao, atual.resultado, presentes);
  }

  /// Nulo se gravou; senão, o motivo (a revisão continua na tela).
  Future<String?> confirmar() async {
    final atual = state;
    if (atual is! Revisando) return null;
    final todos = atual.resultado.alunos.map((a) => a.pessoaId).toSet();
    state = const Confirmando();
    try {
      await _repo.confirmar(atual.sessao.id, presentes: atual.presentes, ausentes: todos.difference(atual.presentes));
      if (ref.mounted) state = ChamadaConfirmada(atual.presentes.length, todos.length);
      return null;
    } on Object catch (erro) {
      if (ref.mounted) state = atual;
      return _mensagem(erro, 'Não foi possível confirmar a chamada.');
    }
  }

  String _mensagem(Object erro, String padrao) {
    final texto = mensagemDeErro(erro, padrao);
    return texto.contains('não ministra') ? 'Você não ministra esta turma.' : texto;
  }
}
