import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../features/auth/data/user.dart';
import '../l10n/l10n.dart';

class Routes {
  static const loading = '/loading';
  static const login = '/login';
  static const faceLogin = '/login/face';
  static const home = '/';
  static const notices = '/notices';
  static const agenda = '/agenda';
  static const reportCard = '/report-card';
  static const dependents = '/dependents';
  static const profile = '/profile';
  static const biometrics = '/profile/biometrics';
  static const faceEnrollment = '/profile/biometrics/enrollment';
  static const benefits = '/benefits';
  static const materials = '/materials';
  static const attendance = '/attendance';

  static String dependent(String studentId) => '$dependents/$studentId';
  static String attendanceOffering(String offeringId) => '$attendance/$offeringId';
  static String attendanceMeeting(String offeringId, String meetingId, {String? pendingId}) =>
      '$attendance/$offeringId/$meetingId${pendingId == null ? '' : '?pending=$pendingId'}';
}

/// As abas do app, na ordem dos ramos do router. Cada pessoa vê só as dos papéis
/// que tem: aluno (agenda, boletim), responsável (dependentes); acumulando, vê todas.
enum AppTab {
  home(Routes.home, Icons.home_outlined, Icons.home_rounded),
  notices(Routes.notices, Icons.notifications_none_rounded, Icons.notifications_rounded),
  agenda(Routes.agenda, Icons.event_note_outlined, Icons.event_note_rounded),
  reportCard(Routes.reportCard, Icons.grading_outlined, Icons.grading_rounded),
  dependents(Routes.dependents, Icons.family_restroom_outlined, Icons.family_restroom_rounded),
  profile(Routes.profile, Icons.person_outline_rounded, Icons.person_rounded);

  const AppTab(this.route, this.icon, this.selectedIcon);
  final String route;
  final IconData icon;
  final IconData selectedIcon;

  String label(AppLocalizations l10n) => switch (this) {
    AppTab.home => l10n.tabHome,
    AppTab.notices => l10n.tabNotices,
    AppTab.agenda => l10n.tabAgenda,
    AppTab.reportCard => l10n.tabReportCard,
    AppTab.dependents => l10n.tabDependents,
    AppTab.profile => l10n.tabProfile,
  };

  bool isVisibleTo(User user) => switch (this) {
    AppTab.agenda || AppTab.reportCard => user.isStudent,
    AppTab.dependents => user.isGuardian,
    _ => true,
  };

  static List<AppTab> forUser(User user) => values.where((tab) => tab.isVisibleTo(user)).toList();

  /// A aba dona de um caminho (`/dependents/123` → dependents).
  static AppTab? ofLocation(String location) =>
      values.where((tab) => tab != AppTab.home && (location == tab.route || location.startsWith('${tab.route}/'))).firstOrNull ??
      (location == Routes.home ? AppTab.home : null);
}

/// Para onde mandar a pessoa, dado o estado da sessão. `null` = pode ficar.
///
/// Fora do GoRouter para poder ser testada sem montar app nenhum.
String? redirect(AsyncValue<User?> auth, String location) {
  final atEntry = location == Routes.login || location == Routes.faceLogin || location == Routes.loading;

  // Ainda conferindo o token salvo, ou falhou ao conferir (sem rede): espera
  // na tela de carregamento, que oferece "tentar de novo".
  if (!auth.hasValue || auth.hasError) {
    return location == Routes.loading ? null : Routes.loading;
  }

  final user = auth.value;
  if (user == null) return location == Routes.login || location == Routes.faceLogin ? null : Routes.login;
  if (atEntry) return Routes.home;

  // Benefícios do próprio aluno (o responsável os vê em cada dependente).
  if (location == Routes.benefits && !user.isStudent) return Routes.home;
  // Requisições de material: quem tem a permissão de pedir (professores, por padrão).
  if (location == Routes.materials && !user.canRequestMaterials) return Routes.home;
  // Chamada facial: quem ministra aulas.
  if ((location == Routes.attendance || location.startsWith('${Routes.attendance}/')) && !user.teaches) return Routes.home;

  // Aba de um papel que a pessoa não tem (ex.: link antigo depois de trocar de papel).
  final tab = AppTab.ofLocation(location);
  return tab != null && !tab.isVisibleTo(user) ? Routes.home : null;
}
