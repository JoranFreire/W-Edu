import '../../../core/network/api_error.dart';
import 'chamada_pendente.dart';
import 'chamada_repository.dart';
import 'fila_de_chamadas.dart';

/// Envia as chamadas da fila quando há rede: abre a sessão no Persona (uma vez) e manda cada foto com
/// o horário em que foi tirada. Cada passo fica gravado, então uma queda no meio não reenvia nada.
class EnvioDeChamadas {
  EnvioDeChamadas(this._fila, this._persona);

  final FilaDeChamadas _fila;
  final ChamadaRepository _persona;

  /// Quantas ficaram prontas para revisão. Sem rede, para e deixa o resto para a próxima vez.
  Future<int> enviarPendentes() async {
    var prontas = 0;
    for (final chamada in await _fila.listar()) {
      if (chamada.enviada) continue;
      try {
        await _enviar(chamada);
        prontas++;
      } on Object catch (erro) {
        if (erroDeRede(erro)) break;
        // Outro problema (ex.: turma que deixou de ministrar): segue com as demais.
      }
    }
    return prontas;
  }

  Future<void> _enviar(ChamadaPendente pendente) async {
    var chamada = pendente;
    if (chamada.sessaoId == null) {
      final sessao = await _persona.abrir(turmaId: chamada.turmaId, encontroId: chamada.encontroId);
      chamada = chamada.copiar(sessaoId: sessao.id);
      await _fila.salvar(chamada);
    }
    for (final foto in chamada.fotos.where((f) => !f.enviada)) {
      final bytes = await _fila.foto(chamada, foto.angulo);
      if (bytes != null) await _persona.enviarFoto(chamada.sessaoId!, foto.angulo, bytes, foto.tiradaEm);
      chamada = chamada.copiar(fotos: [for (final f in chamada.fotos) f.angulo == foto.angulo ? f.marcadaEnviada() : f]);
      await _fila.salvar(chamada);
    }
  }
}
