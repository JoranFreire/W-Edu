import 'dart:convert';
import 'dart:typed_data';

import '../../../shared/vault/file_vault.dart';
import 'attendance_result.dart';
import 'pending_attendance.dart';

/// Chamadas fotografadas sem rede. Tudo no cofre cifrado: o índice (turma, encontro, horários)
/// e as fotos. Some quando a chamada é confirmada ou descartada.
class AttendanceQueue {
  AttendanceQueue(this._vault);

  final FileVault _vault;
  static const _index = 'pending_attendances.json';

  Future<List<PendingAttendance>> list() async {
    final bytes = await _vault.read(_index);
    if (bytes == null) return [];
    final items = jsonDecode(utf8.decode(bytes)) as List<dynamic>;
    return [for (final item in items) PendingAttendance.fromJson(item as Map<String, dynamic>)];
  }

  Future<PendingAttendance?> find(String id) async => (await list()).where((a) => a.id == id).firstOrNull;

  Future<void> save(PendingAttendance attendance) async {
    final others = (await list()).where((a) => a.id != attendance.id);
    await _write([...others, attendance]);
  }

  /// Guarda a foto (cifrada) e a registra na chamada; a mesma posição substitui a anterior.
  Future<PendingAttendance> storePhoto(PendingAttendance attendance, PhotoAngle angle, Uint8List photo, DateTime takenAt) async {
    await _vault.store(attendance.photoName(angle), photo);
    final updated = attendance.copyWith(
      photos: [
        ...attendance.photos.where((p) => p.angle != angle),
        PendingPhoto(angle: angle, takenAt: takenAt),
      ],
    );
    await save(updated);
    return updated;
  }

  Future<Uint8List?> photo(PendingAttendance attendance, PhotoAngle angle) => _vault.read(attendance.photoName(angle));

  /// Apaga as fotos e tira a chamada da fila.
  Future<void> remove(String id) async {
    final all = await list();
    for (final attendance in all.where((a) => a.id == id)) {
      for (final photo in attendance.photos) {
        await _vault.delete(attendance.photoName(photo.angle));
      }
    }
    await _write(all.where((a) => a.id != id).toList());
  }

  Future<void> _write(List<PendingAttendance> attendances) =>
      _vault.store(_index, Uint8List.fromList(utf8.encode(jsonEncode([for (final a in attendances) a.toJson()]))));
}
