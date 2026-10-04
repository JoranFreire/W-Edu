import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:cryptography/cryptography.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:path_provider/path_provider.dart';

/// Arquivos cifrados no aparelho (ex.: fotos da sala esperando a rede). Nada sai daqui em claro:
/// cada arquivo é AES-GCM com uma chave que mora só no armazenamento seguro (Keychain/Keystore).
abstract interface class FileVault {
  Future<void> store(String name, Uint8List content);

  /// Nulo se não existe (ou não decifra: arquivo corrompido ou chave trocada).
  Future<Uint8List?> read(String name);

  Future<void> delete(String name);

  /// Ao sair da conta: nada de outra pessoa fica no aparelho.
  Future<void> deleteAll();
}

class EncryptedFileVault implements FileVault {
  EncryptedFileVault({FlutterSecureStorage? keys, Future<Directory> Function()? folder})
    : _keys = keys ?? const FlutterSecureStorage(),
      _baseFolder = folder ?? getApplicationSupportDirectory;

  static const _keyName = 'vault_aes_gcm';
  final FlutterSecureStorage _keys;
  final Future<Directory> Function() _baseFolder;
  final _aes = AesGcm.with256bits();
  SecretKey? _key;

  Future<SecretKey> _vaultKey() async {
    if (_key != null) return _key!;
    final stored = await _keys.read(key: _keyName);
    if (stored != null) return _key = SecretKey(base64Decode(stored));
    final fresh = await _aes.newSecretKey();
    await _keys.write(key: _keyName, value: base64Encode(await fresh.extractBytes()));
    return _key = fresh;
  }

  Future<File> _file(String name) async {
    final folder = Directory('${(await _baseFolder()).path}/vault');
    await folder.create(recursive: true);
    return File('${folder.path}/${name.replaceAll(RegExp(r'[^A-Za-z0-9_.-]'), '_')}');
  }

  @override
  Future<void> store(String name, Uint8List content) async {
    final box = await _aes.encrypt(content, secretKey: await _vaultKey());
    final file = await _file(name);
    final temp = File('${file.path}.tmp');
    await temp.writeAsBytes(box.concatenation(), flush: true);
    await temp.rename(file.path);
  }

  @override
  Future<Uint8List?> read(String name) async {
    final file = await _file(name);
    if (!await file.exists()) return null;
    try {
      final box = SecretBox.fromConcatenation(
        await file.readAsBytes(),
        nonceLength: _aes.nonceLength,
        macLength: _aes.macAlgorithm.macLength,
      );
      return Uint8List.fromList(await _aes.decrypt(box, secretKey: await _vaultKey()));
    } on Object {
      return null;
    }
  }

  @override
  Future<void> delete(String name) async {
    final file = await _file(name);
    if (await file.exists()) await file.delete();
  }

  @override
  Future<void> deleteAll() async {
    final folder = Directory('${(await _baseFolder()).path}/vault');
    if (await folder.exists()) await folder.delete(recursive: true);
  }
}
