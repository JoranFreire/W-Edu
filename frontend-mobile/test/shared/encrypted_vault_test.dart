import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/shared/vault/file_vault.dart';

void main() {
  late Directory folder;

  setUp(() async {
    FlutterSecureStorage.setMockInitialValues({});
    folder = await Directory.systemTemp.createTemp('vault');
  });

  tearDown(() => folder.delete(recursive: true));

  test('guarda cifrado e lê de volta', () async {
    final vault = EncryptedFileVault(folder: () async => folder);
    final photo = Uint8List.fromList(List.generate(2048, (i) => i % 251));
    await vault.store('attendance_1_CENTER', photo);

    final onDisk = await File('${folder.path}/vault/attendance_1_CENTER').readAsBytes();
    expect(onDisk.length, greaterThan(photo.length), reason: 'nonce e MAC junto');
    expect(_contains(onDisk, photo.sublist(0, 64)), isFalse, reason: 'nada em claro no disco');
    expect(await vault.read('attendance_1_CENTER'), photo);
  });

  test('outra chave não decifra; apagar remove', () async {
    await EncryptedFileVault(folder: () async => folder).store('x', Uint8List.fromList([1, 2, 3]));
    FlutterSecureStorage.setMockInitialValues({});
    final other = EncryptedFileVault(folder: () async => folder);
    expect(await other.read('x'), isNull);
    await other.delete('x');
    expect(await File('${folder.path}/vault/x').exists(), isFalse);
    expect(await other.read('missing'), isNull);
  });
}

bool _contains(List<int> data, List<int> chunk) {
  for (var i = 0; i + chunk.length <= data.length; i++) {
    var equal = true;
    for (var j = 0; j < chunk.length && equal; j++) {
      equal = data[i + j] == chunk[j];
    }
    if (equal) return true;
  }
  return false;
}
