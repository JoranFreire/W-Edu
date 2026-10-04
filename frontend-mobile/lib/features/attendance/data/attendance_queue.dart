import 'dart:convert';
import 'dart:typed_data';

import '../../../shared/vault/file_vault.dart';
import 'pending_attendance.dart';
import 'attendance_result.dart';

/// Chamadas fotografadas sem rede. Tudo no cofre cifrado: o índice (turma, encontro, horários)
/// e as fotos. Some quando a chamada é confirmada ou descartada.
class FilaDeChamadas {
  FilaDeChamadas(this._cofre);

  final CofreDeArquivos _cofre;
  static const _indice = 'chamadas_pendentes.json';

  Future<List<ChamadaPendente>> listar() async {
    final bytes = await _cofre.ler(_indice);
    if (bytes == null) return [];
    final itens = jsonDecode(utf8.decode(bytes)) as List<dynamic>;
    return [for (final item in itens) ChamadaPendente.fromJson(item as Map<String, dynamic>)];
  }

  Future<ChamadaPendente?> buscar(String id) async => (await listar()).where((c) => c.id == id).firstOrNull;

  Future<void> salvar(ChamadaPendente chamada) async {
    final outras = (await listar()).where((c) => c.id != chamada.id);
    await _gravar([...outras, chamada]);
  }

  /// Guarda a foto (cifrada) e a registra na chamada; a mesma posição substitui a anterior.
  Future<ChamadaPendente> guardarFoto(ChamadaPendente chamada, AnguloFoto angulo, Uint8List foto, DateTime tiradaEm) async {
    await _cofre.guardar(chamada.nomeDaFoto(angulo), foto);
    final atualizada = chamada.copiar(fotos: [
      ...chamada.fotos.where((f) => f.angulo != angulo),
      FotoPendente(angulo: angulo, tiradaEm: tiradaEm),
    ]);
    await salvar(atualizada);
    return atualizada;
  }

  Future<Uint8List?> foto(ChamadaPendente chamada, AnguloFoto angulo) => _cofre.ler(chamada.nomeDaFoto(angulo));

  /// Apaga as fotos e tira a chamada da fila.
  Future<void> remover(String id) async {
    final todas = await listar();
    for (final chamada in todas.where((c) => c.id == id)) {
      for (final foto in chamada.fotos) {
        await _cofre.apagar(chamada.nomeDaFoto(foto.angulo));
      }
    }
    await _gravar(todas.where((c) => c.id != id).toList());
  }

  Future<void> _gravar(List<ChamadaPendente> chamadas) =>
      _cofre.guardar(_indice, Uint8List.fromList(utf8.encode(jsonEncode([for (final c in chamadas) c.toJson()]))));
}
