import '../../../core/network/api_error.dart';
import '../../../l10n/l10n.dart';
import '../attendance_flow.dart';
import '../data/attendance_result.dart';

extension PhotoAngleText on PhotoAngle {
  String label(AppLocalizations l10n) => switch (this) {
    PhotoAngle.left => l10n.angleLeft,
    PhotoAngle.center => l10n.angleCenter,
    PhotoAngle.right => l10n.angleRight,
  };
}

extension PhotoOutcomeText on PhotoOutcome {
  String label(AppLocalizations l10n) => switch (this) {
    PhotoOutcome.present => l10n.outcomePresent,
    PhotoOutcome.uncertain => l10n.outcomeUncertain,
    PhotoOutcome.absent => l10n.outcomeAbsent,
    PhotoOutcome.withoutConsent => l10n.outcomeWithoutConsent,
  };
}

extension AttendanceFailedText on AttendanceFailed {
  String message(AppLocalizations l10n) {
    final error = this.error;
    return switch (reason) {
      AttendanceFailure.openFailed when error != null && apiStatusCode(error) == 403 => l10n.attendanceNotTeaching,
      AttendanceFailure.openFailed =>
        error == null ? l10n.attendanceOpenFailed : apiErrorMessage(error, l10n, fallback: l10n.attendanceOpenFailed),
      AttendanceFailure.cameraUnavailable => l10n.attendanceCameraUnavailable,
      AttendanceFailure.notPending => l10n.attendanceNotPending,
      AttendanceFailure.stillOffline => l10n.attendanceStillOffline,
      AttendanceFailure.stillProcessing => l10n.attendanceStillProcessing,
      AttendanceFailure.analysisFailed || AttendanceFailure.resumeFailed =>
        error == null ? l10n.attendanceAnalysisFailed : apiErrorMessage(error, l10n, fallback: l10n.attendanceAnalysisFailed),
    };
  }
}
