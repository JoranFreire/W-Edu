import 'package:flutter/material.dart';

/// Os mesmos tons do site (paleta indigo/gray do Tailwind usada em `frontend/`),
/// para o app e o web terem a mesma cara. Acrescente copiando de lá, não inventando.
class AppColors {
  static const brand50 = Color(0xFFEEF2FF);
  static const brand600 = Color(0xFF4F46E5);
  static const brand700 = Color(0xFF4338CA);

  static const gray50 = Color(0xFFF9FAFB);
  static const gray100 = Color(0xFFF3F4F6);
  static const gray200 = Color(0xFFE5E7EB);
  static const gray400 = Color(0xFF9CA3AF);
  static const gray500 = Color(0xFF6B7280);
  static const gray700 = Color(0xFF374151);
  static const gray800 = Color(0xFF1F2937);
  static const gray900 = Color(0xFF111827);
  static const gray950 = Color(0xFF030712);

  static const emerald600 = Color(0xFF059669);
  static const red600 = Color(0xFFDC2626);
  static const amber700 = Color(0xFFB45309);
  static const sky600 = Color(0xFF0284C7);
  static const violet600 = Color(0xFF7C3AED);
}

/// As cores dos selos (`StatusBadge`/selos do web).
enum BadgeColor {
  blue(AppColors.sky600),
  green(AppColors.emerald600),
  yellow(AppColors.amber700),
  red(AppColors.red600),
  gray(AppColors.gray500),
  purple(AppColors.violet600);

  const BadgeColor(this.color);
  final Color color;
}
