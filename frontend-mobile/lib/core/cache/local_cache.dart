import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// O que fica salvo de uma tela: o JSON bruto da API e a versão da área
/// (`sync/versions`) no momento em que foi baixado. Versão nula = desconhecida
/// (servidor sem versões): na próxima abertura baixa de novo.
class CacheEntry {
  const CacheEntry(this.version, this.data);

  final int? version;
  final Object? data;

  Map<String, Object?> toJson() => {'version': version, 'data': data};

  static CacheEntry? fromJson(Object? json) {
    if (json is! Map<String, dynamic> || !json.containsKey('data')) return null;
    return CacheEntry(json['version'] as int?, json['data']);
  }
}

abstract interface class LocalCache {
  Future<CacheEntry?> read(String key);
  Future<void> save(String key, CacheEntry entry);

  /// Apaga tudo (ao sair da conta: os dados são pessoais).
  Future<void> clear();
}

/// Um arquivo JSON por chave no diretório de suporte do app (não é backup do
/// usuário nem some com "limpar cache" do sistema). Falhas de disco nunca
/// derrubam a tela: ler devolve nulo e salvar é ignorado.
class FileCache implements LocalCache {
  Directory? _folder;

  Future<Directory> _directory() async => _folder ??= Directory('${(await getApplicationSupportDirectory()).path}/wedu_cache');

  Future<File> _file(String key) async => File('${(await _directory()).path}/${key.replaceAll(RegExp(r'[^A-Za-z0-9_-]'), '_')}.json');

  @override
  Future<CacheEntry?> read(String key) async {
    File? file;
    try {
      file = await _file(key);
      if (!await file.exists()) return null;
      final entry = CacheEntry.fromJson(jsonDecode(await file.readAsString()));
      if (entry == null) throw const FormatException('invalid cache');
      return entry;
    } catch (_) {
      // Corrompido: apaga e trata como primeira abertura.
      try {
        await file?.delete();
      } catch (_) {}
      return null;
    }
  }

  @override
  Future<void> save(String key, CacheEntry entry) async {
    try {
      final file = await _file(key);
      await file.parent.create(recursive: true);
      final temp = File('${file.path}.tmp');
      await temp.writeAsString(jsonEncode(entry.toJson()), flush: true);
      await temp.rename(file.path); // troca atômica no mesmo diretório
    } catch (_) {}
  }

  @override
  Future<void> clear() async {
    try {
      final folder = await _directory();
      if (await folder.exists()) await folder.delete(recursive: true);
    } catch (_) {}
  }
}
