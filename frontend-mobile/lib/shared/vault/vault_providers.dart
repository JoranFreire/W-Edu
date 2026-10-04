import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'file_vault.dart';

/// Os testes põem um cofre em memória.
final fileVaultProvider = Provider<FileVault>((ref) => EncryptedFileVault());
