// Junta os textos de cada funcionalidade (`lib/**/l10n/<parte>_<idioma>.arb`) no ARB que o
// gen-l10n lê (`lib/l10n/generated/app_<idioma>.arb`). Rode depois de mexer em qualquer parte:
//   dart run tool/merge_arb.dart
// Chave repetida entre partes é erro: cada texto tem um dono só.
import 'dart:convert';
import 'dart:io';

const locales = ['pt', 'en'];
const output = 'lib/l10n/generated';

void main() {
  for (final locale in locales) {
    final merged = mergeLocale(locale);
    File('$output/app_$locale.arb')
      ..createSync(recursive: true)
      ..writeAsStringSync(encode(merged));
  }
  stdout.writeln('ARB gerado em $output');
}

/// As partes de um idioma, em ordem estável (comum primeiro, depois as features por nome).
List<File> parts(String locale) {
  final suffix = '_$locale.arb';
  final files = Directory('lib')
      .listSync(recursive: true)
      .whereType<File>()
      .where((f) => f.path.endsWith(suffix) && f.parent.path.endsWith('l10n') && !f.path.contains('/generated/'))
      .toList();
  return files..sort((a, b) => a.path.compareTo(b.path));
}

Map<String, Object?> mergeLocale(String locale) {
  final merged = <String, Object?>{'@@locale': locale};
  final owners = <String, String>{};
  for (final file in parts(locale)) {
    final entries = jsonDecode(file.readAsStringSync()) as Map<String, Object?>;
    for (final MapEntry(:key, :value) in entries.entries) {
      if (key.startsWith('@@')) continue;
      final owner = owners[key];
      if (owner != null) throw StateError('Chave "$key" repetida em ${file.path} e $owner');
      owners[key] = file.path;
      merged[key] = value;
    }
  }
  return merged;
}

String encode(Map<String, Object?> arb) => '${const JsonEncoder.withIndent('  ').convert(arb)}\n';
