import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cofre_de_arquivos.dart';

/// Os testes põem um cofre em memória.
final cofreProvider = Provider<CofreDeArquivos>((ref) => CofreCifrado());
