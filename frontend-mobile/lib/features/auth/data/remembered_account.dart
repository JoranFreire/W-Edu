import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'user.dart';

/// A última conta que entrou neste aparelho: o login facial é 1:1 (a pessoa diz
/// quem é e o rosto é comparado só com o dela), então o app precisa lembrar quem.
/// Sobrevive ao "Sair" (só o token e os dados das telas são apagados).
class ContaLembrada {
  const ContaLembrada({required this.usuarioId, required this.instituicaoId, required this.nome, required this.email});

  final String usuarioId;
  final String instituicaoId;
  final String nome;
  final String email;

  String get primeiroNome => nome.split(' ').first;

  factory ContaLembrada.de(Usuario usuario) =>
      ContaLembrada(usuarioId: usuario.id, instituicaoId: usuario.instituicao.id, nome: usuario.nome, email: usuario.email);

  Map<String, String> toJson() => {'usuario_id': usuarioId, 'instituicao_id': instituicaoId, 'nome': nome, 'email': email};

  factory ContaLembrada.fromJson(Map<String, dynamic> json) => ContaLembrada(
        usuarioId: json['usuario_id'] as String,
        instituicaoId: json['instituicao_id'] as String,
        nome: json['nome'] as String,
        email: json['email'] as String,
      );
}

abstract interface class ContaLembradaStore {
  Future<ContaLembrada?> ler();
  Future<void> salvar(ContaLembrada conta);

  /// "Usar outra conta": o aparelho deixa de oferecer o rosto para esta pessoa.
  Future<void> esquecer();
}

class SecureContaLembradaStore implements ContaLembradaStore {
  SecureContaLembradaStore([FlutterSecureStorage? storage]) : _storage = storage ?? const FlutterSecureStorage();

  static const _chave = 'conta_lembrada';
  final FlutterSecureStorage _storage;

  @override
  Future<ContaLembrada?> ler() async {
    final texto = await _storage.read(key: _chave);
    if (texto == null) return null;
    try {
      return ContaLembrada.fromJson(jsonDecode(texto) as Map<String, dynamic>);
    } on Object {
      await esquecer();
      return null;
    }
  }

  @override
  Future<void> salvar(ContaLembrada conta) => _storage.write(key: _chave, value: jsonEncode(conta.toJson()));

  @override
  Future<void> esquecer() => _storage.delete(key: _chave);
}
