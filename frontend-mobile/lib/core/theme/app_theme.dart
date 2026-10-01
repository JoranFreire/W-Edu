import 'package:flutter/material.dart';

import 'app_colors.dart';

class AppTheme {
  static ThemeData get claro => _tema(
        ColorScheme.fromSeed(
          seedColor: AppColors.brand600,
          primary: AppColors.brand600,
          error: AppColors.red600,
          surface: Colors.white,
          onSurface: AppColors.gray900,
          onSurfaceVariant: AppColors.gray500,
          outlineVariant: AppColors.gray200,
        ),
        fundo: AppColors.gray50,
      );

  static ThemeData get escuro => _tema(
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
        fundo: AppColors.gray950,
      );

  static ThemeData _tema(ColorScheme cores, {required Color fundo}) {
    final borda = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
      side: BorderSide(color: cores.outlineVariant),
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: cores,
      scaffoldBackgroundColor: fundo,
      appBarTheme: AppBarTheme(
        backgroundColor: fundo,
        foregroundColor: cores.onSurface,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(color: cores.surface, elevation: 0, margin: EdgeInsets.zero, shape: borda),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: cores.surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: cores.outlineVariant),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          // Só a altura: largura mínima infinita quebra o botão dentro de Row.
          minimumSize: const Size(64, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: cores.surface,
        indicatorColor: cores.primary.withValues(alpha: 0.12),
      ),
    );
  }
}
