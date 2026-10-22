import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import '../../tool/merge_arb.dart' as arb;

/// Os textos moram em cada funcionalidade (`lib/**/l10n/<parte>_<idioma>.arb`); o ARB do gen-l10n
/// é só a junção. Estes testes pegam parte esquecida, junção desatualizada e idioma incompleto.
void main() {
  for (final locale in arb.locales) {
    test('ARB gerado em $locale está em dia com as partes (rode dart run tool/merge_arb.dart)', () {
      final generated = File('${arb.output}/app_$locale.arb').readAsStringSync();
      expect(generated, arb.encode(arb.mergeLocale(locale)));
    });
  }

  test('cada parte tem as mesmas chaves em todos os idiomas', () {
    Set<String> keys(File file) =>
        (jsonDecode(file.readAsStringSync()) as Map<String, Object?>).keys.where((k) => !k.startsWith('@')).toSet();
    final template = arb.parts('pt');
    for (final locale in arb.locales.skip(1)) {
      final translated = arb.parts(locale);
      expect(translated.map((f) => f.path.replaceAll('_$locale.arb', '')), template.map((f) => f.path.replaceAll('_pt.arb', '')));
      for (final (index, file) in template.indexed) {
        expect(keys(translated[index]), keys(file), reason: '${translated[index].path} diferente de ${file.path}');
      }
    }
  });
}
