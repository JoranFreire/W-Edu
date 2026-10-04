import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/cache/areas.dart';
import '../../core/cache/watch_area.dart';
import '../../core/network/api_error.dart';
import '../../core/network/network_providers.dart';
import '../../shared/vault/vault_providers.dart';
import '../../shared/face/face.dart';
import '../auth/auth_providers.dart';
import 'data/pending_attendance.dart';
import 'data/attendance_repository.dart';
import 'data/teaching.dart';
import 'data/teaching_repository.dart';
import 'data/attendance_uploader.dart';
import 'data/attendance_queue.dart';
import 'data/attendance_result.dart';

final docenciaRepositoryProvider = Provider<DocenciaRepository>((ref) => DocenciaRepository(ref.watch(dioProvider)));

/// Nulo quando o Persona não está configurado.
final chamadaRepositoryProvider = Provider<ChamadaRepository?>((ref) {
  final dio = ref.watch(personaDioProvider);
  return dio == null ? null : ChamadaRepository(dio);
});

abstract final class ChavesDocencia {
  static const turmas = 'docencia_turmas';
  static String encontros(String turmaId) => 'docencia_encontros_$turmaId';
}

/// Turmas e encontros em cache: sem rede, o professor ainda escolhe o encontro e fotografa a sala.
final turmasDocenteProvider = StreamProvider<List<TurmaDocente>>((ref) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesDocencia.turmas,
      area: Areas.docencia,
      baixar: ref.watch(docenciaRepositoryProvider).turmas,
      ler: TurmaDocente.lista,
    ));

final encontrosProvider = StreamProvider.family<List<Encontro>, String>((ref, turmaId) => observarArea(
      ref,
      dono: ref.watch(donoDoCacheProvider),
      chave: ChavesDocencia.encontros(turmaId),
      area: Areas.docencia,
      baixar: () => ref.read(docenciaRepositoryProvider).encontros(turmaId),
      ler: Encontro.abertos,
    ));

final filaDeChamadasProvider = Provider<FilaDeChamadas>((ref) => FilaDeChamadas(ref.watch(cofreProvider)));

/// Chamadas fotografadas sem rede: tenta enviar ao abrir e quando pedirem ("Enviar agora", voltar ao app).
final chamadasPendentesProvider = AsyncNotifierProvider.autoDispose<ChamadasPendentes, List<ChamadaPendente>>(ChamadasPendentes.new);

class ChamadasPendentes extends AsyncNotifier<List<ChamadaPendente>> {
  @override
  Future<List<ChamadaPendente>> build() async {
    final pendentes = await ref.read(filaDeChamadasProvider).listar();
    if (pendentes.any((c) => !c.enviada)) Future.microtask(enviar);
    return pendentes;
  }

  /// Quantas ficaram prontas para revisão.
  Future<int> enviar() async {
    final persona = ref.read(chamadaRepositoryProvider);
    if (persona == null) return 0;
    final prontas = await EnvioDeChamadas(ref.read(filaDeChamadasProvider), persona).enviarPendentes();
    if (ref.mounted) state = AsyncData(await ref.read(filaDeChamadasProvider).listar());
    return prontas;
  }

  Future<void> descartar(String id) async {
    await ref.read(filaDeChamadasProvider).remover(id);
    if (ref.mounted) state = AsyncData(await ref.read(filaDeChamadasProvider).listar());
  }
}

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

/// Sem rede ao abrir: dá para fotografar agora e enviar depois.
class SemRede extends EtapaChamada {
  const SemRede();
}

class Fotografando extends EtapaChamada {
  const Fotografando(this.sessao, this.enviadas, {this.enviando, this.pendente});

  /// Nula sem rede: as fotos vão para a fila cifrada ([pendente]).
  final SessaoChamada? sessao;
  final ChamadaPendente? pendente;
  final Set<AnguloFoto> enviadas;
  final AnguloFoto? enviando;
}

/// Fotos guardadas sem rede; a chamada segue quando a internet voltar.
class FotosGuardadas extends EtapaChamada {
  const FotosGuardadas(this.quantidade);
  final int quantidade;
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

/// `pendenteId`: chamada que estava na fila (já enviada ou não), aberta para seguir até a revisão.
typedef ChaveChamada = ({String turmaId, String encontroId, String? pendenteId});

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
    Future.microtask(chave.pendenteId == null ? _abrir : _retomar);
    return chave.pendenteId == null ? const AbrindoSessao() : const Processando();
  }

  FilaDeChamadas get _fila => ref.read(filaDeChamadasProvider);

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
      if (!ref.mounted) return;
      state = erroDeRede(erro) ? const SemRede() : ChamadaFalhou(_mensagem(erro, 'Não foi possível abrir a chamada.'));
    }
  }

  /// Sem rede: as fotos vão cifradas para a fila e seguem quando a internet voltar.
  Future<void> fotografarSemRede() async {
    if (state is! SemRede) return;
    try {
      final CapturaDeRosto camera = ref.read(cameraDeSalaProvider);
      _camera = camera;
      await camera.abrir();
      _cameraAberta = true;
      final pendente = ChamadaPendente(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        turmaId: chave.turmaId,
        encontroId: chave.encontroId,
        titulo: _titulo(),
        criadaEm: DateTime.now(),
      );
      if (ref.mounted) state = Fotografando(null, const {}, pendente: pendente);
    } on Object {
      if (ref.mounted) state = const ChamadaFalhou('Não foi possível abrir a câmera. Confira a permissão do app.');
    }
  }

  /// Chamada da fila: envia o que faltar e abre a revisão.
  Future<void> _retomar() async {
    var pendente = await _fila.buscar(chave.pendenteId!);
    if (pendente == null) {
      if (ref.mounted) state = const ChamadaFalhou('Esta chamada não está mais pendente.');
      return;
    }
    try {
      if (!pendente.enviada) {
        await EnvioDeChamadas(_fila, _repo).enviarPendentes();
        pendente = await _fila.buscar(pendente.id);
      }
      if (pendente == null || !pendente.enviada) {
        if (ref.mounted) state = const ChamadaFalhou('Ainda sem internet. As fotos continuam guardadas e seguem quando a rede voltar.');
        return;
      }
      await _analisar(SessaoChamada(id: pendente.sessaoId!, comAutorizacao: 0, semAutorizacao: 0));
    } on Object catch (erro) {
      if (ref.mounted) state = ChamadaFalhou(_mensagem(erro, 'Não foi possível retomar a chamada.'));
    }
  }

  String _titulo() {
    final turma = ref.read(turmasDocenteProvider).value?.where((t) => t.id == chave.turmaId).firstOrNull?.nome;
    final encontro = ref.read(encontrosProvider(chave.turmaId)).value?.where((e) => e.id == chave.encontroId).firstOrNull?.titulo;
    return [turma ?? 'Turma', encontro ?? 'Encontro'].join(' · ');
  }

  /// Nulo se a foto foi enviada; senão, o motivo (a tela avisa e a pessoa tenta de novo).
  Future<String?> fotografar(AnguloFoto angulo) async {
    final atual = state;
    if (atual is! Fotografando || atual.enviando != null || !_cameraAberta) return null;
    state = Fotografando(atual.sessao, atual.enviadas, enviando: angulo, pendente: atual.pendente);
    try {
      final foto = await _camera!.fotografar();
      final tiradaEm = DateTime.now();
      final sessao = atual.sessao;
      var pendente = atual.pendente;
      if (sessao != null) {
        await _repo.enviarFoto(sessao.id, angulo, foto, tiradaEm);
      } else {
        pendente = await _fila.guardarFoto(pendente!, angulo, foto, tiradaEm);
      }
      if (ref.mounted) state = Fotografando(sessao, {...atual.enviadas, angulo}, pendente: pendente);
      return null;
    } on Object catch (erro) {
      if (ref.mounted) state = Fotografando(atual.sessao, atual.enviadas, pendente: atual.pendente);
      return _mensagem(erro, 'Não foi possível enviar a foto.');
    }
  }

  /// Espera o Persona processar todas as fotos e abre a revisão.
  /// Sem rede, só guarda (a análise vem quando a fila for enviada).
  Future<void> analisar() async {
    final atual = state;
    if (atual is! Fotografando || atual.enviadas.isEmpty) return;
    await _camera?.fechar();
    _cameraAberta = false;
    final sessao = atual.sessao;
    if (sessao == null) {
      ref.invalidate(chamadasPendentesProvider);
      state = FotosGuardadas(atual.enviadas.length);
      return;
    }
    state = const Processando();
    await _analisar(sessao);
  }

  Future<void> _analisar(SessaoChamada sessao) async {
    try {
      for (var consulta = 0; consulta < _maximoDeConsultas; consulta++) {
        final resultado = await _repo.resultado(sessao.id);
        if (!ref.mounted) return;
        if (resultado.fotosPendentes == 0) {
          final reconhecidos = resultado.de(SituacaoNaFoto.presente).map((a) => a.pessoaId).toSet();
          state = Revisando(sessao, resultado, reconhecidos);
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
      // Confirmada: as fotos guardadas no aparelho já não servem para nada.
      if (chave.pendenteId != null) await _fila.remover(chave.pendenteId!);
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
