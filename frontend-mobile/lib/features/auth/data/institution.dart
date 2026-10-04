import 'package:flutter/material.dart';

/// A instituição ativa da sessão (a do token), com a marca dela.
class Instituicao {
  const Instituicao({required this.id, required this.slug, required this.nome, this.corPrimaria});

  final String id;
  final String slug;
  final String nome;

  /// Cor principal da instituição (`branding.primary_color`), quando cadastrada.
  final Color? corPrimaria;

  factory Instituicao.fromJson(Map<String, dynamic> json) {
    final marca = json['branding'] as Map<String, dynamic>? ?? const {};
    final nomeExibido = (marca['display_name'] as String?)?.trim();
    return Instituicao(
      id: json['id'] as String,
      slug: json['slug'] as String,
      nome: nomeExibido != null && nomeExibido.isNotEmpty ? nomeExibido : json['name'] as String,
      corPrimaria: _cor(marca['primary_color'] as String?),
    );
  }

  static Color? _cor(String? hex) {
    if (hex == null || !RegExp(r'^#[0-9a-fA-F]{6}$').hasMatch(hex)) return null;
    return Color(int.parse('FF${hex.substring(1)}', radix: 16));
  }
}
