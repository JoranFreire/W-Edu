import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/shared/vault/file_vault.dart';

void main() {
  late Directory pasta;

  setUp(() async {
    FlutterSecureStorage.setMockInitialValues({});
    pasta = await Directory.systemTemp.createTemp('cofre');
  });

  tearDown(() => pasta.delete(recursive: true));

  test('guarda cifrado e lê de volta', () async {
    final cofre = CofreCifrado(pasta: () async => pasta);
    final foto = Uint8List.fromList(List.generate(2048, (i) => i % 251));
    await cofre.guardar('chamada_1_CENTER', foto);

    final noDisco = await File('${pasta.path}/cofre/chamada_1_CENTER').readAsBytes();
    expect(noDisco.length, greaterThan(foto.length), reason: 'nonce e MAC junto');
    expect(_contem(noDisco, foto.sublist(0, 64)), isFalse, reason: 'nada em claro no disco');
    expect(await cofre.ler('chamada_1_CENTER'), foto);
  });

  test('outra chave não decifra; apagar remove', () async {
    await CofreCifrado(pasta: () async => pasta).guardar('x', Uint8List.fromList([1, 2, 3]));
    FlutterSecureStorage.setMockInitialValues({});
    final outro = CofreCifrado(pasta: () async => pasta);
    expect(await outro.ler('x'), isNull);
    await outro.apagar('x');
    expect(await File('${pasta.path}/cofre/x').exists(), isFalse);
    expect(await outro.ler('nada'), isNull);
  });
}

bool _contem(List<int> dados, List<int> trecho) {
  for (var i = 0; i + trecho.length <= dados.length; i++) {
    var igual = true;
    for (var j = 0; j < trecho.length && igual; j++) {
      igual = dados[i + j] == trecho[j];
    }
    if (igual) return true;
  }
  return false;
}
