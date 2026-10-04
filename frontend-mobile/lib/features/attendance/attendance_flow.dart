import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_error.dart';
import '../../shared/face/face.dart';
import 'attendance_providers.dart';
import 'data/attendance_queue.dart';
import 'data/attendance_repository.dart';
import 'data/attendance_result.dart';
import 'data/attendance_uploader.dart';
import 'attendance_steps.dart';

export 'attendance_steps.dart';
import 'data/pending_attendance.dart';

/// Intervalo entre as consultas do resultado enquanto o Persona processa as fotos (zero nos testes).
final resultPollIntervalProvider = Provider<Duration>((ref) => const Duration(seconds: 2));
const _maxPolls = 90;

/// `pendingId`: chamada que estava na fila (já enviada ou não), aberta para seguir até a revisão.
typedef AttendanceKey = ({String offeringId, String meetingId, String? pendingId});

final attendanceFlowProvider = NotifierProvider.autoDispose.family<AttendanceFlow, AttendanceStep, AttendanceKey>(AttendanceFlow.new);

/// Chamada facial de um encontro. O resultado nunca vale sozinho: o professor revisa e confirma,
/// e só então o Persona grava e repassa ao W-Edu.
class AttendanceFlow extends Notifier<AttendanceStep> {
  AttendanceFlow(this.key);

  final AttendanceKey key;
  DeviceCameraCapture? _camera;
  bool _cameraOpen = false;

  @override
  AttendanceStep build() {
    ref.onDispose(() => _camera?.close());
    Future.microtask(key.pendingId == null ? _open : _resume);
    return key.pendingId == null ? const AttendanceOpening() : const AttendanceProcessing();
  }

  AttendanceQueue get _queue => ref.read(attendanceQueueProvider);

  AttendanceRepository get _repo => ref.read(attendanceRepositoryProvider)!;

  /// A câmera traseira (vazia antes de abrir).
  DeviceCameraCapture? get camera => _camera;

  Future<void> _open() async {
    try {
      final session = await _repo.open(offeringId: key.offeringId, meetingId: key.meetingId);
      if (!ref.mounted) return;
      await _openCamera();
      if (ref.mounted) state = AttendancePhotographing(session, const {});
    } on Object catch (error) {
      if (!ref.mounted) return;
      state = isNetworkError(error) ? const AttendanceOffline() : AttendanceFailed(AttendanceFailure.openFailed, error);
    }
  }

  Future<void> _openCamera() async {
    final DeviceCameraCapture camera = ref.read(roomCameraProvider);
    _camera = camera;
    await camera.open();
    _cameraOpen = true;
  }

  /// Sem rede: as fotos vão cifradas para a fila e seguem quando a internet voltar.
  Future<void> photographOffline() async {
    if (state is! AttendanceOffline) return;
    try {
      await _openCamera();
      final pending = PendingAttendance(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        offeringId: key.offeringId,
        meetingId: key.meetingId,
        title: _title(),
        createdAt: DateTime.now(),
      );
      if (ref.mounted) state = AttendancePhotographing(null, const {}, pending: pending);
    } on Object {
      if (ref.mounted) state = const AttendanceFailed(AttendanceFailure.cameraUnavailable);
    }
  }

  /// Chamada da fila: envia o que faltar e abre a revisão.
  Future<void> _resume() async {
    var pending = await _queue.find(key.pendingId!);
    if (pending == null) {
      if (ref.mounted) state = const AttendanceFailed(AttendanceFailure.notPending);
      return;
    }
    try {
      if (!pending.isUploaded) {
        await AttendanceUploader(_queue, _repo).uploadPending();
        pending = await _queue.find(pending.id);
      }
      if (pending == null || !pending.isUploaded) {
        if (ref.mounted) state = const AttendanceFailed(AttendanceFailure.stillOffline);
        return;
      }
      await _analyze(AttendanceSession(id: pending.sessionId!, withConsent: 0, withoutConsent: 0));
    } on Object catch (error) {
      if (ref.mounted) state = AttendanceFailed(AttendanceFailure.resumeFailed, error);
    }
  }

  /// Turma e encontro (dos dados em cache), para o professor reconhecer a chamada guardada.
  String _title() {
    final offering = ref.read(teachingOfferingsProvider).value?.where((o) => o.id == key.offeringId).firstOrNull?.name;
    final meeting = ref.read(meetingsProvider(key.offeringId)).value?.where((m) => m.id == key.meetingId).firstOrNull?.title;
    return [?offering, ?meeting].join(' · ');
  }

  /// Nulo se a foto foi enviada (ou guardada); senão, o erro (a tela avisa e a pessoa tenta de novo).
  Future<Object?> takePhoto(PhotoAngle angle) async {
    final current = state;
    if (current is! AttendancePhotographing || current.sending != null || !_cameraOpen) return null;
    state = AttendancePhotographing(current.session, current.taken, sending: angle, pending: current.pending);
    try {
      final photo = await _camera!.takePhoto();
      final takenAt = DateTime.now();
      final session = current.session;
      var pending = current.pending;
      if (session != null) {
        await _repo.uploadPhoto(session.id, angle, photo, takenAt);
      } else {
        pending = await _queue.storePhoto(pending!, angle, photo, takenAt);
      }
      if (ref.mounted) state = AttendancePhotographing(session, {...current.taken, angle}, pending: pending);
      return null;
    } on Object catch (error) {
      if (ref.mounted) state = AttendancePhotographing(current.session, current.taken, pending: current.pending);
      return error;
    }
  }

  /// Espera o Persona processar todas as fotos e abre a revisão.
  /// Sem rede, só guarda (a análise vem quando a fila for enviada).
  Future<void> analyze() async {
    final current = state;
    if (current is! AttendancePhotographing || current.taken.isEmpty) return;
    await _camera?.close();
    _cameraOpen = false;
    final session = current.session;
    if (session == null) {
      ref.invalidate(pendingAttendancesProvider);
      state = AttendancePhotosSaved(current.taken.length);
      return;
    }
    state = const AttendanceProcessing();
    await _analyze(session);
  }

  Future<void> _analyze(AttendanceSession session) async {
    try {
      for (var poll = 0; poll < _maxPolls; poll++) {
        final result = await _repo.result(session.id);
        if (!ref.mounted) return;
        if (result.pendingImages == 0) {
          final recognized = result.withOutcome(PhotoOutcome.present).map((s) => s.personId).toSet();
          state = AttendanceReviewing(session, result, recognized);
          return;
        }
        await Future<void>.delayed(ref.read(resultPollIntervalProvider));
      }
      state = const AttendanceFailed(AttendanceFailure.stillProcessing);
    } on Object catch (error) {
      if (ref.mounted) state = AttendanceFailed(AttendanceFailure.analysisFailed, error);
    }
  }

  void toggle(String personId) {
    final current = state;
    if (current is! AttendanceReviewing) return;
    final present = {...current.present};
    present.contains(personId) ? present.remove(personId) : present.add(personId);
    state = AttendanceReviewing(current.session, current.result, present);
  }

  /// Nulo se gravou; senão, o erro (a revisão continua na tela).
  Future<Object?> confirm() async {
    final current = state;
    if (current is! AttendanceReviewing) return null;
    final everyone = current.result.students.map((s) => s.personId).toSet();
    state = const AttendanceConfirming();
    try {
      await _repo.confirm(current.session.id, present: current.present, absent: everyone.difference(current.present));
      // Confirmada: as fotos guardadas no aparelho já não servem para nada.
      if (key.pendingId != null) await _queue.remove(key.pendingId!);
      if (ref.mounted) state = AttendanceConfirmed(current.present.length, everyone.length);
      return null;
    } on Object catch (error) {
      if (ref.mounted) state = current;
      return error;
    }
  }
}
