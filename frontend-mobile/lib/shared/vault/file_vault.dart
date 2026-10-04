import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:cryptography/cryptography.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:path_provider/path_provider.dart';

/// Arquivos cifrados no aparelho (ex.: fotos da sala esperando a rede). Nada sai daqui em claro:
/// cada arquivo é AES-GCM com uma chave que mora só no armazenamento seguro (Keychain/Keystore).
abstract interface class CofreDeArquivos {
  Future<void> guardar(String nome, Uint8List conteudo);

  /// Nulo se não existe (ou não decifra: arquivo corrompido ou chave trocada).
  Future<Uint8List?> ler(String nome);

  Future<void> apagar(String nome);

  /// Ao sair da conta: nada de outra pessoa fica no aparelho.
  Future<void> apagarTudo();
}

class CofreCifrado implements CofreDeArquivos {
  CofreCifrado({FlutterSecureStorage? chaves, Future<Directory> Function()? pasta})
      : _chaves = chaves ?? const FlutterSecureStorage(),
        _pastaBase = pasta ?? getApplicationSupportDirectory;

  static const _nomeDaChave = 'cofre_aes_gcm';
  final FlutterSecureStorage _chaves;
  final Future<Directory> Function() _pastaBase;
  final _aes = AesGcm.with256bits();
  SecretKey? _chave;

  Future<SecretKey> _chaveDoCofre() async {
    if (_chave != null) return _chave!;
    final guardada = await _chaves.read(key: _nomeDaChave);
    if (guardada != null) return _chave = SecretKey(base64Decode(guardada));
    final nova = await _aes.newSecretKey();
    await _chaves.write(key: _nomeDaChave, value: base64Encode(await nova.extractBytes()));
    return _chave = nova;
  }

  Future<File> _arquivo(String nome) async {
    final pasta = Directory('${(await _pastaBase()).path}/cofre');
    await pasta.create(recursive: true);
    return File('${pasta.path}/${nome.replaceAll(RegExp(r'[^A-Za-z0-9_.-]'), '_')}');
  }

  @override
  Future<void> guardar(String nome, Uint8List conteudo) async {
    final caixa = await _aes.encrypt(conteudo, secretKey: await _chaveDoCofre());
    final arquivo = await _arquivo(nome);
    final temporario = File('${arquivo.path}.tmp');
    await temporario.writeAsBytes(caixa.concatenation(), flush: true);
    await temporario.rename(arquivo.path);
  }

  @override
  Future<Uint8List?> ler(String nome) async {
    final arquivo = await _arquivo(nome);
    if (!await arquivo.exists()) return null;
    try {
      final caixa = SecretBox.fromConcatenation(
        await arquivo.readAsBytes(),
        nonceLength: _aes.nonceLength,
        macLength: _aes.macAlgorithm.macLength,
      );
      return Uint8List.fromList(await _aes.decrypt(caixa, secretKey: await _chaveDoCofre()));
    } on Object {
      return null;
    }
  }

  @override
  Future<void> apagar(String nome) async {
    final arquivo = await _arquivo(nome);
    if (await arquivo.exists()) await arquivo.delete();
  }

  @override
  Future<void> apagarTudo() async {
    final pasta = Directory('${(await _pastaBase()).path}/cofre');
    if (await pasta.exists()) await pasta.delete(recursive: true);
  }
}
