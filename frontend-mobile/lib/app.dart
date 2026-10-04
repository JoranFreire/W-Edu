import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import 'core/cache/revalidate_on_resume.dart';
import 'core/config/locale_providers.dart';
import 'core/theme/app_theme.dart';
import 'l10n/l10n.dart';
import 'router/app_router.dart';

class WEduApp extends ConsumerWidget {
  const WEduApp({super.key});

  static const fallbackLocale = Locale('pt', 'BR');

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      onGenerateTitle: (context) => context.l10n.appTitle,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      routerConfig: ref.watch(routerProvider),
      locale: ref.watch(appLocaleProvider),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      localeResolutionCallback: _resolveLocale,
      builder: (context, child) {
        // Datas e números (DateFormat) seguem o idioma da tela.
        Intl.defaultLocale = Localizations.localeOf(context).toLanguageTag().replaceAll('-', '_');
        return RevalidateOnResume(child: child!);
      },
    );
  }

  /// Idioma do aparelho quando o app o tem; senão, português.
  static Locale _resolveLocale(Locale? device, Iterable<Locale> supported) {
    if (device == null) return fallbackLocale;
    return supported.where((l) => l.languageCode == device.languageCode).firstOrNull ?? fallbackLocale;
  }
}
