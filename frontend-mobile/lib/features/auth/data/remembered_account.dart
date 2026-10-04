import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'user.dart';

/// A última conta que entrou neste aparelho: o login facial é 1:1 (a pessoa diz
/// quem é e o rosto é comparado só com o dela), então o app precisa lembrar quem.
/// Sobrevive ao "Sair" (só o token e os dados das telas são apagados).
class RememberedAccount {
  const RememberedAccount({required this.userId, required this.institutionId, required this.name, required this.email});

  final String userId;
  final String institutionId;
  final String name;
  final String email;

  String get firstName => name.split(' ').first;

  factory RememberedAccount.of(User user) =>
      RememberedAccount(userId: user.id, institutionId: user.institution.id, name: user.name, email: user.email);

  Map<String, String> toJson() => {'user_id': userId, 'institution_id': institutionId, 'name': name, 'email': email};

  factory RememberedAccount.fromJson(Map<String, dynamic> json) => RememberedAccount(
    userId: json['user_id'] as String,
    institutionId: json['institution_id'] as String,
    name: json['name'] as String,
    email: json['email'] as String,
  );
}

abstract interface class RememberedAccountStore {
  Future<RememberedAccount?> read();
  Future<void> save(RememberedAccount account);

  /// "Usar outra conta": o aparelho deixa de oferecer o rosto para esta pessoa.
  Future<void> forget();
}

class SecureRememberedAccountStore implements RememberedAccountStore {
  SecureRememberedAccountStore([FlutterSecureStorage? storage]) : _storage = storage ?? const FlutterSecureStorage();

  static const _key = 'remembered_account';
  final FlutterSecureStorage _storage;

  @override
  Future<RememberedAccount?> read() async {
    final text = await _storage.read(key: _key);
    if (text == null) return null;
    try {
      return RememberedAccount.fromJson(jsonDecode(text) as Map<String, dynamic>);
    } on Object {
      await forget();
      return null;
    }
  }

  @override
  Future<void> save(RememberedAccount account) => _storage.write(key: _key, value: jsonEncode(account.toJson()));

  @override
  Future<void> forget() => _storage.delete(key: _key);
}
