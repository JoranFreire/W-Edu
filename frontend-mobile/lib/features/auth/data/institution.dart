import 'package:flutter/material.dart';

/// A instituição ativa da sessão (a do token), com a marca dela.
class Institution {
  const Institution({required this.id, required this.slug, required this.name, this.primaryColor});

  final String id;
  final String slug;
  final String name;

  /// Cor principal da instituição (`branding.primary_color`), quando cadastrada.
  final Color? primaryColor;

  factory Institution.fromJson(Map<String, dynamic> json) {
    final branding = json['branding'] as Map<String, dynamic>? ?? const {};
    final displayName = (branding['display_name'] as String?)?.trim();
    return Institution(
      id: json['id'] as String,
      slug: json['slug'] as String,
      name: displayName != null && displayName.isNotEmpty ? displayName : json['name'] as String,
      primaryColor: _color(branding['primary_color'] as String?),
    );
  }

  static Color? _color(String? hex) {
    if (hex == null || !RegExp(r'^#[0-9a-fA-F]{6}$').hasMatch(hex)) return null;
    return Color(int.parse('FF${hex.substring(1)}', radix: 16));
  }
}
