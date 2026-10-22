import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Idioma do app: nulo segue o aparelho (com pt-BR quando não houver tradução).
/// Os testes fixam pt-BR.
final appLocaleProvider = Provider<Locale?>((ref) => null);
