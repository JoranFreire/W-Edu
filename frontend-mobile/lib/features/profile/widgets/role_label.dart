import '../../../l10n/l10n.dart';

/// Os nomes dos papéis, iguais aos do site.
String roleLabel(String role, AppLocalizations l10n) => switch (role) {
  'student' => l10n.roleStudent,
  'instructor' => l10n.roleInstructor,
  'coordinator' => l10n.roleCoordinator,
  'secretary' => l10n.roleSecretary,
  'guardian' => l10n.roleGuardian,
  'company_manager' => l10n.roleCompanyManager,
  'institution_admin' => l10n.roleInstitutionAdmin,
  'admin' => l10n.roleAdmin,
  'super_admin' => l10n.roleSuperAdmin,
  _ => role,
};
