import 'package:flutter/material.dart';

/// Para que o rosto pode ser usado. Cada uma é autorizada (e revogada) separadamente:
/// revogar uma não desliga a outra (ADR 0010 do Persona).
enum Purpose {
  login('LOGIN', Icons.face_rounded),
  access('ACCESS', Icons.door_sliding_rounded),
  attendance('ATTENDANCE', Icons.how_to_reg_rounded);

  const Purpose(this.value, this.icon);
  final String value;
  final IconData icon;

  /// O responsável autoriza, pelo dependente menor de 16, só login e catraca.
  bool get guardianMayConsent => this != Purpose.attendance;

  static Purpose? of(String value) => values.where((p) => p.value == value).firstOrNull;
}
