import 'package:flutter/material.dart';

import '../../../core/format/dates.dart';
import '../../../core/theme/app_colors.dart';

enum BenefitStatus {
  released('released', BadgeColor.green),
  redeemed('redeemed', BadgeColor.blue),
  cancelled('cancelled', BadgeColor.gray),
  expired('expired', BadgeColor.yellow);

  const BenefitStatus(this.value, this.color);
  final String value;
  final BadgeColor color;

  static BenefitStatus of(String value) => values.firstWhere((s) => s.value == value, orElse: () => cancelled);
}

/// O que é o benefício (mesmos tipos do catálogo do backend).
enum BenefitKind {
  snack('snack', Icons.lunch_dining_rounded),
  material('material', Icons.backpack_rounded),
  uniform('uniform', Icons.checkroom_rounded),
  transport('transport', Icons.directions_bus_rounded),
  stipend('stipend', Icons.payments_rounded),
  other('other', Icons.redeem_rounded);

  const BenefitKind(this.value, this.icon);
  final String value;
  final IconData icon;

  static BenefitKind of(String? value) => values.firstWhere((k) => k.value == value, orElse: () => other);
}

/// Benefício liberado para retirada com QR (lanche, kit de material, uniforme, vale-transporte...).
class Benefit {
  const Benefit({
    required this.id,
    required this.code,
    required this.qrPayload,
    required this.serverStatus,
    required this.item,
    required this.kind,
    required this.quantity,
    required this.unit,
    required this.offeringName,
    required this.releasedAt,
    this.validUntil,
    this.redeemedAt,
  });

  final String id;
  final String code;
  final String qrPayload;
  final BenefitStatus serverStatus;
  final String item;
  final BenefitKind kind;
  final int quantity;
  final String unit;
  final String offeringName;
  final DateTime releasedAt;
  final DateTime? validUntil;
  final DateTime? redeemedAt;

  /// Do cache, um liberado pode ter vencido desde o download: a validade vale também offline.
  BenefitStatus status([DateTime? now]) {
    final today = DateUtils.dateOnly(now ?? DateTime.now());
    final expired = validUntil != null && validUntil!.isBefore(today);
    return serverStatus == BenefitStatus.released && expired ? BenefitStatus.expired : serverStatus;
  }

  bool get isReadyForPickup => status() == BenefitStatus.released;

  /// Lista da API (ou do cache): os que estão para retirar primeiro, depois o histórico.
  static List<Benefit> list(Object? json) {
    final items = [for (final item in json as List<dynamic>) Benefit.fromJson(item as Map<String, dynamic>)];
    return [...items.where((b) => b.isReadyForPickup), ...items.where((b) => !b.isReadyForPickup)];
  }

  factory Benefit.fromJson(Map<String, dynamic> json) {
    final validUntil = json['valid_until'] as String?;
    final redeemedAt = json['redeemed_at'] as String?;
    return Benefit(
      id: json['id'] as String,
      code: json['code'] as String,
      qrPayload: json['qr_payload'] as String,
      serverStatus: BenefitStatus.of(json['status'] as String),
      item: json['item_name'] as String,
      kind: BenefitKind.of(json['item_kind'] as String?),
      quantity: json['quantity'] as int,
      unit: json['unit'] as String? ?? 'unidade',
      offeringName: json['class_offering_name'] as String? ?? '',
      releasedAt: DateTime.parse(json['released_at'] as String),
      validUntil: validUntil == null ? null : parseDay(validUntil),
      redeemedAt: redeemedAt == null ? null : DateTime.parse(redeemedAt),
    );
  }
}
