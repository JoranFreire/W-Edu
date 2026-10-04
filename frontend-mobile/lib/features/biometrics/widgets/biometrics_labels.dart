import '../../../core/network/api_error.dart';
import '../../../l10n/l10n.dart';
import '../data/purpose.dart';

extension PurposeText on Purpose {
  String label(AppLocalizations l10n) => switch (this) {
    Purpose.login => l10n.purposeLogin,
    Purpose.access => l10n.purposeAccess,
    Purpose.attendance => l10n.purposeAttendance,
  };

  String hint(AppLocalizations l10n) => switch (this) {
    Purpose.login => l10n.purposeLoginHint,
    Purpose.access => l10n.purposeAccessHint,
    Purpose.attendance => l10n.purposeAttendanceHint,
  };
}

/// O Persona responde com códigos (`detail`); aqui viram frases para a pessoa.
String personaErrorMessage(Object error, AppLocalizations l10n, {String? fallback}) {
  final message = switch (apiErrorCode(error)) {
    'adult_only' => l10n.personaAdultOnly,
    'guardian_consents' => l10n.personaGuardianConsents,
    'subject_decides_alone' => l10n.personaSubjectDecidesAlone,
    'subject_is_adult' => l10n.personaSubjectIsAdult,
    'guardian_purpose_not_allowed' => l10n.personaGuardianPurposeNotAllowed,
    'terms_outdated' => l10n.personaTermsOutdated,
    'institution_required' => l10n.personaInstitutionRequired,
    'no_active_consent' => l10n.personaNoActiveConsent,
    'challenge_invalid' => l10n.personaChallengeInvalid,
    _ => null,
  };
  if (message != null) return message;
  if (apiStatusCode(error) == 422) return l10n.personaFaceNotChecked;
  return apiErrorMessage(error, l10n, fallback: fallback);
}
