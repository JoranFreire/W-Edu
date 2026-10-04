// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get agendaTitle => 'School agenda';

  @override
  String get agendaEmpty => 'Nothing on the agenda yet.';

  @override
  String get agendaKindHomework => 'Homework';

  @override
  String get agendaKindTest => 'Test';

  @override
  String get agendaKindEvent => 'Event';

  @override
  String get agendaKindNotice => 'Notice';

  @override
  String get attendanceTitle => 'Face attendance';

  @override
  String get attendanceNoClasses => 'No classes for you.';

  @override
  String get attendanceChooseMeeting => 'Choose the meeting';

  @override
  String get attendanceNoMeetings => 'No open meetings in this class.';

  @override
  String get attendanceOpening => 'Opening attendance…';

  @override
  String get attendanceAnalyzing => 'Analyzing the photos…';

  @override
  String get attendanceSaving => 'Saving attendance…';

  @override
  String get attendanceOffline =>
      'No internet right now. You can photograph the room: the photos stay stored (encrypted) on the device and attendance is analyzed when the connection is back.';

  @override
  String get attendancePhotographLater => 'Photograph and send later';

  @override
  String attendancePhotosSaved(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count photos saved', one: '1 photo saved');
    return '$_temp0. When the internet is back, open Face attendance to send and review.';
  }

  @override
  String attendanceConfirmed(int present, int total) {
    return 'Attendance saved: $present present out of $total.';
  }

  @override
  String get attendanceBackToMeetings => 'Back to meetings';

  @override
  String get attendanceNotTeaching => 'You don\'t teach this class.';

  @override
  String get attendanceOpenFailed => 'Could not open attendance.';

  @override
  String get attendanceCameraUnavailable => 'Could not open the camera.';

  @override
  String get attendanceNotPending => 'This attendance is no longer stored on the device.';

  @override
  String get attendanceStillOffline => 'Still offline: the photos stay stored to send later.';

  @override
  String get attendanceStillProcessing => 'The photos are still being analyzed. Try again shortly.';

  @override
  String get attendanceAnalysisFailed => 'Could not analyze the photos.';

  @override
  String get attendancePhotoFailed => 'Could not send the photo.';

  @override
  String get attendanceConfirmFailed => 'Could not save attendance.';

  @override
  String get angleLeft => 'Left side';

  @override
  String get angleCenter => 'Center';

  @override
  String get angleRight => 'Right side';

  @override
  String get attendanceOfflineHint => 'Offline: the photos stay stored (encrypted) and attendance is analyzed when the connection is back.';

  @override
  String attendanceWithConsent(int count) {
    return '$count student(s) with recognition authorized';
  }

  @override
  String attendanceWithoutConsent(int count) {
    return ' · $count without (you mark them in the review)';
  }

  @override
  String attendanceAnalyze(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count photos', one: '1 photo');
    return 'Analyze $_temp0';
  }

  @override
  String attendanceStore(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count photos', one: '1 photo');
    return 'Store $_temp0';
  }

  @override
  String get outcomePresent => 'Recognized';

  @override
  String get outcomeUncertain => 'Check';

  @override
  String get outcomeAbsent => 'Not found in the photos';

  @override
  String get outcomeWithoutConsent => 'Recognition not authorized (mark by hand)';

  @override
  String outcomeSection(String title, int count) {
    return '$title ($count)';
  }

  @override
  String get inThePhoto => 'In the photo';

  @override
  String attendanceConfirm(int present, int total) {
    return 'Confirm attendance: $present present out of $total';
  }

  @override
  String get pendingDiscardTitle => 'Discard this attendance?';

  @override
  String pendingDiscardBody(String title) {
    return 'The photos of $title will be deleted from the device without sending.';
  }

  @override
  String get discard => 'Discard';

  @override
  String pendingStored(int count) {
    return 'Attendances stored on the device ($count)';
  }

  @override
  String get sendNow => 'Send now';

  @override
  String pendingSummary(int count, String date, String state) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count photos', one: '1 photo');
    return '$_temp0 · $date · $state';
  }

  @override
  String get pendingReady => 'ready to review';

  @override
  String get pendingWaiting => 'waiting for internet';

  @override
  String get enrollmentPhoto => 'Enrollment';

  @override
  String get signInWithAnotherAccount => 'Sign in with another account';

  @override
  String get loginSubtitle => 'Sign in with your institution account';

  @override
  String get emailLabel => 'Email';

  @override
  String get emailRequired => 'Enter your email.';

  @override
  String get passwordLabel => 'Password';

  @override
  String get passwordRequired => 'Enter your password.';

  @override
  String get showPassword => 'Show password';

  @override
  String get hidePassword => 'Hide password';

  @override
  String get signIn => 'Sign in';

  @override
  String get signInError => 'Could not sign in.';

  @override
  String faceSignInAs(String name) {
    return 'Sign in with your face as $name';
  }

  @override
  String notYouUseAnotherAccount(String name) {
    return 'Not $name? Use another account';
  }

  @override
  String get faceLoginTitle => 'Sign in with your face';

  @override
  String faceLoginHello(String name) {
    return 'Hi, $name';
  }

  @override
  String get faceLoginIntro => 'Let\'s check it\'s you.\nYou will look at the camera and turn your face to both sides.';

  @override
  String get faceChecking => 'Checking…';

  @override
  String get signInWithPassword => 'Sign in with password';

  @override
  String get faceLoginUnavailable => 'Face sign-in is not available. Use your password.';

  @override
  String get faceLoginCameraUnavailable => 'Could not open the camera. Check the permission or use your password.';

  @override
  String get faceLoginRefused => 'Could not sign in with your face. Use your password.';

  @override
  String get benefitsTitle => 'Benefits';

  @override
  String get benefitsEmpty => 'No benefits released.';

  @override
  String get benefitStatusReleased => 'Released';

  @override
  String get benefitStatusRedeemed => 'Picked up';

  @override
  String get benefitStatusCancelled => 'Cancelled';

  @override
  String get benefitStatusExpired => 'Expired';

  @override
  String get benefitKindSnack => 'Snack';

  @override
  String get benefitKindMaterial => 'Material';

  @override
  String get benefitKindUniform => 'Uniform';

  @override
  String get benefitKindTransport => 'Transport';

  @override
  String get benefitKindStipend => 'Stipend';

  @override
  String get benefitKindOther => 'Other';

  @override
  String benefitRedeemedOn(String date) {
    return 'Picked up on $date';
  }

  @override
  String benefitPickUpBy(String date) {
    return 'Pick up by $date';
  }

  @override
  String benefitReleasedOn(String date) {
    return 'Released on $date';
  }

  @override
  String get showQr => 'Show QR code';

  @override
  String get benefitNoExpiry => 'No expiry date';

  @override
  String benefitValidUntil(String date) {
    return 'Valid until $date';
  }

  @override
  String benefitQrFooter(String validity) {
    return '$validity\nShow this QR code at pickup.';
  }

  @override
  String get purposeLogin => 'Sign in to the app with your face';

  @override
  String get purposeLoginHint => 'Use your face instead of your password when opening the app.';

  @override
  String get purposeAccess => 'Turnstile';

  @override
  String get purposeAccessHint => 'Go through the institution\'s turnstile with your face (your guardian gets a notice).';

  @override
  String get purposeAttendance => 'Class attendance';

  @override
  String get purposeAttendanceHint => 'The teacher takes attendance with a photo of the room. Only for people aged 18 or over.';

  @override
  String get personaAdultOnly =>
      'Face attendance is only for people aged 18 or over. If your date of birth is wrong, contact the school office.';

  @override
  String get personaGuardianConsents =>
      'Until age 16, your guardian gives the consent. If your date of birth is wrong, contact the school office.';

  @override
  String get personaSubjectDecidesAlone => 'From age 16, the student consents in the app.';

  @override
  String get personaSubjectIsAdult => 'The student is an adult: they consent in the app.';

  @override
  String get personaGuardianPurposeNotAllowed => 'Guardians can only consent to sign-in and turnstile.';

  @override
  String get personaTermsOutdated => 'The terms were updated. Read the new version and consent again.';

  @override
  String get personaInstitutionRequired => 'Sign in again and try once more.';

  @override
  String get personaNoActiveConsent => 'Consent to at least one use of your face before enrolling it.';

  @override
  String get personaChallengeInvalid => 'The check timed out. Try again.';

  @override
  String get personaFaceNotChecked => 'Could not check your face (lighting, framing or movements). Try again.';

  @override
  String get biometricsTitle => 'Face recognition';

  @override
  String get biometricsIntro =>
      'Each use is consented separately and can be revoked at any time. Your password (and the front desk, at the turnstile) always remains available.';

  @override
  String get enrollmentTitle => 'Enroll your face';

  @override
  String get enrollmentIntro =>
      'In a well-lit place, look at the camera and turn your face to both sides when asked. The photos are only used for the check and are not kept on the device.';

  @override
  String get enrollmentDone => 'Face enrolled.';

  @override
  String get finish => 'Done';

  @override
  String get enrollmentUnavailable => 'Face recognition is not available.';

  @override
  String get enrollmentCameraUnavailable => 'Could not open the camera. Check the app permission.';

  @override
  String get enrollmentError => 'Could not enroll your face.';

  @override
  String get faceEnrolled => 'Your face is enrolled.';

  @override
  String get faceEnrollmentMissing => 'Enroll your face to use what you consented to.';

  @override
  String get faceEnrollmentNeedsConsent => 'Consent to at least one use below to enroll your face.';

  @override
  String get reenrollFace => 'Enroll your face again';

  @override
  String get enrollMyFace => 'Enroll my face';

  @override
  String get consentAdultsOnly => 'Only for people aged 18 or over.';

  @override
  String get consentGuardianDecides => 'Until age 16, your guardian consents in their app.';

  @override
  String consentGranted(String purpose) {
    return '$purpose: consented.';
  }

  @override
  String consentRevoked(String purpose) {
    return '$purpose: revoked.';
  }

  @override
  String get dependentDecidesAlone => 'From age 16, the student consents to the use of their face in the app.';

  @override
  String dependentFaceEnrolled(String name) {
    return '$name\'s face is enrolled.';
  }

  @override
  String dependentEnrollAfterConsent(String name) {
    return 'After you consent, $name enrolls their own face in the app (Profile → Face recognition).';
  }

  @override
  String termsOnBehalfOf(String name) {
    return 'Consent on behalf of $name';
  }

  @override
  String termsVersion(String version) {
    return 'Terms version $version';
  }

  @override
  String get termsAgree => 'I have read and agree';

  @override
  String get notNow => 'Not now';

  @override
  String revokeTitle(String purpose) {
    return 'Revoke: $purpose?';
  }

  @override
  String get revokeBody => 'Your face stops being used for this right away. If no use remains consented, your face enrollment is deleted.';

  @override
  String get revoke => 'Revoke';

  @override
  String get dependentsTitle => 'My dependents';

  @override
  String get dependentsEmpty => 'No students linked to your account. Contact the school office.';

  @override
  String get dependentFallbackName => 'Dependent';

  @override
  String get dependentTabFace => 'Face';

  @override
  String get dependentTabBenefits => 'Benefits';

  @override
  String get financialBadge => 'Financial';

  @override
  String get relationshipMother => 'Mother';

  @override
  String get relationshipFather => 'Father';

  @override
  String get relationshipLegalGuardian => 'Legal guardian';

  @override
  String get relationshipGrandparent => 'Grandparent';

  @override
  String get relationshipOther => 'Guardian';

  @override
  String get tabHome => 'Home';

  @override
  String get tabNotices => 'Notices';

  @override
  String get tabAgenda => 'Agenda';

  @override
  String get tabReportCard => 'Report card';

  @override
  String get tabDependents => 'Dependents';

  @override
  String get tabProfile => 'Profile';

  @override
  String homeGreeting(String name) {
    return 'Hi, $name!';
  }

  @override
  String get homeAllRead => 'All read';

  @override
  String homeUnread(int count) {
    return '$count unread';
  }

  @override
  String get homeTapToSee => 'Tap to see';

  @override
  String get homeNextOnAgenda => 'Next on the agenda';

  @override
  String get homeNothingAhead => 'Nothing ahead';

  @override
  String homeNextItem(String title, String date) {
    return '$title · $date';
  }

  @override
  String get homeFaceAttendance => 'Face attendance';

  @override
  String get homeAttendanceHint => 'Photograph the room and review';

  @override
  String homeAttendancePending(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count attendances saved on the device',
      one: '1 attendance saved on the device',
    );
    return '$_temp0';
  }

  @override
  String get homeNothingToPickUp => 'Nothing to pick up';

  @override
  String homeToPickUp(int count) {
    return '$count to pick up';
  }

  @override
  String get homeNoDependents => 'None linked';

  @override
  String get materialsTitle => 'Material requests';

  @override
  String get materialsEmpty => 'No requests. Request materials on the website.';

  @override
  String get materialStatusPending => 'Awaiting approval';

  @override
  String get materialStatusApproved => 'Approved: pick up';

  @override
  String get materialStatusRejected => 'Rejected';

  @override
  String get materialStatusDelivered => 'Picked up';

  @override
  String get materialStatusClosed => 'Closed';

  @override
  String get materialStatusCancelled => 'Cancelled';

  @override
  String get materialReturnOverdue => 'Return overdue';

  @override
  String materialNeededOn(String date) {
    return 'For $date';
  }

  @override
  String materialReturnBy(String date) {
    return 'return by $date';
  }

  @override
  String materialLine(String material, int quantity, String unit) {
    return '$material: $quantity $unit';
  }

  @override
  String materialLineToReturn(String line, int count) {
    return '$line · return $count';
  }

  @override
  String get pickupQr => 'Pickup QR code';

  @override
  String get materialQrFooter => 'Show this QR code at the storeroom. Only you receive this code.';

  @override
  String get noticesTitle => 'Notices';

  @override
  String get markAllAsRead => 'Mark all as read';

  @override
  String get noNotices => 'No notices yet.';

  @override
  String get profileTitle => 'Profile';

  @override
  String get profileEmail => 'Email';

  @override
  String profileRole(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: 'Roles', one: 'Role');
    return '$_temp0';
  }

  @override
  String get profileInstitution => 'Institution';

  @override
  String get profileFaceRecognition => 'Face recognition';

  @override
  String get profileFaceRecognitionHint => 'Face sign-in, turnstile and attendance: consents and face enrollment';

  @override
  String get signOut => 'Sign out';

  @override
  String get signOutTitle => 'Sign out?';

  @override
  String get signOutBody => 'You will need to sign in again with email and password.';

  @override
  String signOutPendingAttendance(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: 'There are $count attendances with photos not yet sent: they will be deleted from the device.',
      one: 'There is 1 attendance with photos not yet sent: it will be deleted from the device.',
    );
    return '$_temp0';
  }

  @override
  String get roleStudent => 'Student';

  @override
  String get roleInstructor => 'Instructor';

  @override
  String get roleCoordinator => 'Coordinator';

  @override
  String get roleSecretary => 'School office';

  @override
  String get roleGuardian => 'Guardian';

  @override
  String get roleCompanyManager => 'Company manager';

  @override
  String get roleInstitutionAdmin => 'Institution admin';

  @override
  String get roleAdmin => 'Admin';

  @override
  String get roleSuperAdmin => 'Platform admin';

  @override
  String get reportCardTitle => 'Report card';

  @override
  String get reportCardEmpty => 'No grades published yet.';

  @override
  String get reportCardNoPeriods => 'No closed periods yet.';

  @override
  String reportCardAbsences(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count absences', one: '1 absence');
    return '$_temp0';
  }

  @override
  String reportCardFinalGrade(String grade) {
    return 'Final grade: $grade';
  }

  @override
  String reportCardRecovery(String grade) {
    return 'Recovery: $grade';
  }

  @override
  String reportCardAttendance(String rate) {
    return 'Attendance: $rate';
  }

  @override
  String reportCardPassingGrade(String grade) {
    return 'Passing grade: $grade';
  }

  @override
  String get subjectInProgress => 'In progress';

  @override
  String get subjectRecovery => 'In recovery';

  @override
  String get subjectApproved => 'Passed';

  @override
  String get subjectFailed => 'Failed';

  @override
  String get subjectFailedAttendance => 'Failed for absences';

  @override
  String get appTitle => 'W-Edu';

  @override
  String get errorGeneric => 'Something went wrong.';

  @override
  String get errorNoConnection => 'No connection to the server. Check your internet.';

  @override
  String get errorTimeout => 'The server took too long to respond.';

  @override
  String get tryAgain => 'Try again';

  @override
  String get back => 'Back';

  @override
  String get cancel => 'Cancel';

  @override
  String get keep => 'Keep';

  @override
  String get close => 'Close';

  @override
  String get errorLoad => 'Could not load.';

  @override
  String get errorRefresh => 'Could not refresh.';

  @override
  String get faceStepCenter => 'Look at the camera';

  @override
  String get faceStepTurnLeft => 'Turn your face to the left';

  @override
  String get faceStepTurnRight => 'Turn your face to the right';

  @override
  String faceStepProgress(int current, int total) {
    return 'Step $current of $total';
  }

  @override
  String qrSemanticLabel(String title) {
    return 'QR code for $title';
  }

  @override
  String get openingCamera => 'Opening the camera…';

  @override
  String get start => 'Start';
}
