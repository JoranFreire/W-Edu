import 'data/attendance_result.dart';
import 'data/pending_attendance.dart';

/// Por que a chamada parou (a tela traduz; [AttendanceFailed.error] traz o erro da API, quando há).
enum AttendanceFailure { openFailed, cameraUnavailable, notPending, stillOffline, stillProcessing, analysisFailed, resumeFailed }

/// Etapas da chamada de um encontro.
sealed class AttendanceStep {
  const AttendanceStep();
}

class AttendanceOpening extends AttendanceStep {
  const AttendanceOpening();
}

/// Sem rede ao abrir: dá para fotografar agora e enviar depois.
class AttendanceOffline extends AttendanceStep {
  const AttendanceOffline();
}

class AttendancePhotographing extends AttendanceStep {
  const AttendancePhotographing(this.session, this.taken, {this.sending, this.pending});

  /// Nula sem rede: as fotos vão para a fila cifrada ([pending]).
  final AttendanceSession? session;
  final PendingAttendance? pending;
  final Set<PhotoAngle> taken;
  final PhotoAngle? sending;
}

/// Fotos guardadas sem rede; a chamada segue quando a internet voltar.
class AttendancePhotosSaved extends AttendanceStep {
  const AttendancePhotosSaved(this.count);
  final int count;
}

class AttendanceProcessing extends AttendanceStep {
  const AttendanceProcessing();
}

class AttendanceReviewing extends AttendanceStep {
  const AttendanceReviewing(this.session, this.result, this.present);
  final AttendanceSession session;
  final AttendanceResult result;

  /// Quem será confirmado presente (começa com os reconhecidos; o professor ajusta).
  final Set<String> present;
}

class AttendanceConfirming extends AttendanceStep {
  const AttendanceConfirming();
}

class AttendanceConfirmed extends AttendanceStep {
  const AttendanceConfirmed(this.present, this.total);
  final int present;
  final int total;
}

class AttendanceFailed extends AttendanceStep {
  const AttendanceFailed(this.reason, [this.error]);
  final AttendanceFailure reason;
  final Object? error;
}
