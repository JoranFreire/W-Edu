import 'package:flutter/material.dart';

import 'app_colors.dart';

class AppTheme {
  static ThemeData get light => _theme(
    ColorScheme.fromSeed(
      seedColor: AppColors.brand600,
      primary: AppColors.brand600,
      error: AppColors.red600,
      surface: Colors.white,
      onSurface: AppColors.gray900,
      onSurfaceVariant: AppColors.gray500,
      outlineVariant: AppColors.gray200,
    ),
    background: AppColors.gray50,
  );

  static ThemeData get dark => _theme(
    ColorScheme.fromSeed(
      seedColor: AppColors.brand600,
      brightness: Brightness.dark,
      primary: AppColors.brand600,
      onPrimary: Colors.white,
      error: AppColors.red600,
      surface: AppColors.gray900,
      onSurface: AppColors.gray100,
      onSurfaceVariant: AppColors.gray400,
      outlineVariant: AppColors.gray800,
    ),
    background: AppColors.gray950,
  );

  static ThemeData _theme(ColorScheme colors, {required Color background}) {
    final border = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
      side: BorderSide(color: colors.outlineVariant),
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colors,
      scaffoldBackgroundColor: background,
      appBarTheme: AppBarTheme(
        backgroundColor: background,
        foregroundColor: colors.onSurface,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(color: colors.surface, elevation: 0, margin: EdgeInsets.zero, shape: border),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colors.surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.outlineVariant),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          // Só a altura: largura mínima infinita quebra o botão dentro de Row.
          minimumSize: const Size(64, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(backgroundColor: colors.surface, indicatorColor: colors.primary.withValues(alpha: 0.12)),
    );
  }
}
