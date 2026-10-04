import '../../../core/format/dates.dart';
import '../../../core/theme/app_colors.dart';

enum MaterialRequestStatus {
  pending('pending', BadgeColor.yellow),
  approved('approved', BadgeColor.purple),
  rejected('rejected', BadgeColor.red),
  delivered('delivered', BadgeColor.blue),
  closed('closed', BadgeColor.green),
  cancelled('cancelled', BadgeColor.gray);

  const MaterialRequestStatus(this.value, this.color);
  final String value;
  final BadgeColor color;

  static MaterialRequestStatus of(String value) => values.firstWhere((s) => s.value == value, orElse: () => cancelled);
}

class MaterialRequestLine {
  const MaterialRequestLine({
    required this.material,
    required this.unit,
    required this.requested,
    this.approved,
    required this.delivered,
    required this.onLoan,
  });

  final String material;
  final String unit;
  final int requested;
  final int? approved;
  final int delivered;

  /// Permanentes ainda fora do almoxarifado (a devolver).
  final int onLoan;

  /// O que vale agora: retirado, senão aprovado, senão pedido.
  int get currentQuantity => delivered > 0 ? delivered : approved ?? requested;

  factory MaterialRequestLine.fromJson(Map<String, dynamic> json) => MaterialRequestLine(
    material: json['item_name'] as String,
    unit: json['unit'] as String,
    requested: json['quantity_requested'] as int,
    approved: json['quantity_approved'] as int?,
    delivered: json['quantity_delivered'] as int,
    onLoan: json['outstanding'] as int,
  );
}

/// Requisição de material ao almoxarifado, de quem pediu: aprovada, traz o QR de retirada.
class MaterialRequest {
  const MaterialRequest({
    required this.id,
    required this.purpose,
    required this.neededOn,
    required this.status,
    required this.lines,
    this.offeringName,
    this.returnDueOn,
    this.overdue = false,
    this.decisionNote,
    this.pickupCode,
    this.qrPayload,
  });

  final String id;
  final String purpose;
  final DateTime neededOn;
  final MaterialRequestStatus status;
  final List<MaterialRequestLine> lines;
  final String? offeringName;
  final DateTime? returnDueOn;
  final bool overdue;
  final String? decisionNote;
  final String? pickupCode;
  final String? qrPayload;

  bool get isReadyForPickup => status == MaterialRequestStatus.approved && qrPayload != null;

  /// As aprovadas (para retirar) primeiro; depois na ordem da API (mais recentes).
  static List<MaterialRequest> list(Object? json) {
    final items = [for (final item in json as List<dynamic>) MaterialRequest.fromJson(item as Map<String, dynamic>)];
    return [...items.where((r) => r.isReadyForPickup), ...items.where((r) => !r.isReadyForPickup)];
  }

  factory MaterialRequest.fromJson(Map<String, dynamic> json) {
    final returnDue = json['return_due_on'] as String?;
    return MaterialRequest(
      id: json['id'] as String,
      purpose: json['purpose'] as String,
      neededOn: parseDay(json['needed_on'] as String),
      status: MaterialRequestStatus.of(json['status'] as String),
      lines: [for (final line in json['lines'] as List<dynamic>) MaterialRequestLine.fromJson(line as Map<String, dynamic>)],
      offeringName: json['class_offering_name'] as String?,
      returnDueOn: returnDue == null ? null : parseDay(returnDue),
      overdue: json['overdue'] as bool? ?? false,
      decisionNote: json['decision_note'] as String?,
      pickupCode: json['pickup_code'] as String?,
      qrPayload: json['qr_payload'] as String?,
    );
  }
}
