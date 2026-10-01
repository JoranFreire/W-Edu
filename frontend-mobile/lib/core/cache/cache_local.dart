import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// O que fica salvo de uma tela: o JSON bruto da API e a versão da área
/// (`sync/versions`) no momento em que foi baixado. Versão nula = desconhecida
/// (servidor sem versões): na próxima abertura baixa de novo.
class EntradaCache {
  const EntradaCache(this.versao, this.dados);

  final int? versao;
  final Object? dados;

  Map<String, Object?> toJson() => {'versao': versao, 'dados': dados};

  static EntradaCache? fromJson(Object? json) {
    if (json is! Map<String, dynamic> || !json.containsKey('dados')) return null;
    return EntradaCache(json['versao'] as int?, json['dados']);
  }
}

abstract interface class CacheLocal {
  Future<EntradaCache?> ler(String chave);
  Future<void> salvar(String chave, EntradaCache entrada);

  /// Apaga tudo (ao sair da conta: os dados são pessoais).
  Future<void> limpar();
}

/// Um arquivo JSON por chave no diretório de suporte do app (não é backup do
/// usuário nem some com "limpar cache" do sistema). Falhas de disco nunca
/// derrubam a tela: ler devolve nulo e salvar é ignorado.
class CacheEmArquivo implements CacheLocal {
  Directory? _pasta;

  Future<Directory> _diretorio() async =>
      _pasta ??= Directory('${(await getApplicationSupportDirectory()).path}/wedu_cache');

  Future<File> _arquivo(String chave) async =>
      File('${(await _diretorio()).path}/${chave.replaceAll(RegExp(r'[^A-Za-z0-9_-]'), '_')}.json');

  @override
  Future<EntradaCache?> ler(String chave) async {
    File? arquivo;
    try {
      arquivo = await _arquivo(chave);
      if (!await arquivo.exists()) return null;
      final entrada = EntradaCache.fromJson(jsonDecode(await arquivo.readAsString()));
      if (entrada == null) throw const FormatException('cache inválido');
      return entrada;
    } catch (_) {
      // Corrompido: apaga e trata como primeira abertura.
      try {
        await arquivo?.delete();
      } catch (_) {}
      return null;
    }
  }

  @override
  Future<void> salvar(String chave, EntradaCache entrada) async {
    try {
      final arquivo = await _arquivo(chave);
      await arquivo.parent.create(recursive: true);
      final temporario = File('${arquivo.path}.tmp');
      await temporario.writeAsString(jsonEncode(entrada.toJson()), flush: true);
      await temporario.rename(arquivo.path); // troca atômica no mesmo diretório
    } catch (_) {}
  }

  @override
  Future<void> limpar() async {
    try {
      final pasta = await _diretorio();
      if (await pasta.exists()) await pasta.delete(recursive: true);
    } catch (_) {}
  }
}
