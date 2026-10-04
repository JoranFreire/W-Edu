import '../../../core/network/api_error.dart';
import 'attendance_queue.dart';
import 'attendance_repository.dart';
import 'pending_attendance.dart';

/// Envia as chamadas da fila quando há rede: abre a sessão no Persona (uma vez) e manda cada foto com
/// o horário em que foi tirada. Cada passo fica gravado, então uma queda no meio não reenvia nada.
class AttendanceUploader {
  AttendanceUploader(this._queue, this._persona);

  final AttendanceQueue _queue;
  final AttendanceRepository _persona;

  /// Quantas ficaram prontas para revisão. Sem rede, para e deixa o resto para a próxima vez.
  Future<int> uploadPending() async {
    var ready = 0;
    for (final attendance in await _queue.list()) {
      if (attendance.isUploaded) continue;
      try {
        await _upload(attendance);
        ready++;
      } on Object catch (error) {
        if (isNetworkError(error)) break;
        // Outro problema (ex.: turma que deixou de ministrar): segue com as demais.
      }
    }
    return ready;
  }

  Future<void> _upload(PendingAttendance pending) async {
    var attendance = pending;
    if (attendance.sessionId == null) {
      final session = await _persona.open(offeringId: attendance.offeringId, meetingId: attendance.meetingId);
      attendance = attendance.copyWith(sessionId: session.id);
      await _queue.save(attendance);
    }
    for (final photo in attendance.photos.where((p) => !p.uploaded)) {
      final bytes = await _queue.photo(attendance, photo.angle);
      if (bytes != null) await _persona.uploadPhoto(attendance.sessionId!, photo.angle, bytes, photo.takenAt);
      attendance = attendance.copyWith(photos: [for (final p in attendance.photos) p.angle == photo.angle ? p.markedUploaded() : p]);
      await _queue.save(attendance);
    }
  }
}
