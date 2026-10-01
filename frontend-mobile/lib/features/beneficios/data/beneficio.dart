import 'package:flutter/material.dart';

import '../../../core/format/datas.dart';
import '../../../core/theme/app_colors.dart';

enum SituacaoBeneficio {
  liberado('released', 'Liberado', BadgeCor.verde),
  retirado('redeemed', 'Retirado', BadgeCor.azul),
  cancelado('cancelled', 'Cancelado', BadgeCor.cinza),
  vencido('expired', 'Vencido', BadgeCor.amarelo);

  const SituacaoBeneficio(this.valor, this.nome, this.cor);
  final String valor;
  final String nome;
  final BadgeCor cor;

  static SituacaoBeneficio de(String valor) => values.firstWhere((s) => s.valor == valor, orElse: () => cancelado);
}

/// O que é o benefício (mesmos tipos do catálogo do backend).
enum TipoBeneficio {
  lanche('snack', 'Lanche', Icons.lunch_dining_rounded),
  material('material', 'Material', Icons.backpack_rounded),
  uniforme('uniform', 'Uniforme', Icons.checkroom_rounded),
  transporte('transport', 'Transporte', Icons.directions_bus_rounded),
  auxilio('stipend', 'Auxílio financeiro', Icons.payments_rounded),
  outro('other', 'Outro', Icons.redeem_rounded);

  const TipoBeneficio(this.valor, this.nome, this.icone);
  final String valor;
  final String nome;
  final IconData icone;

  static TipoBeneficio de(String? valor) => values.firstWhere((t) => t.valor == valor, orElse: () => outro);
}

/// Benefício liberado para retirada com QR (lanche, kit de material, uniforme, vale-transporte...).
class Beneficio {
  const Beneficio({
    required this.id,
    required this.codigo,
    required this.conteudoQr,
    required this.situacaoNoServidor,
    required this.item,
    required this.tipo,
    required this.quantidade,
    required this.unidade,
    required this.turma,
    required this.liberadoEm,
    this.validoAte,
    this.retiradoEm,
  });

  final String id;
  final String codigo;
  final String conteudoQr;
  final SituacaoBeneficio situacaoNoServidor;
  final String item;
  final TipoBeneficio tipo;
  final int quantidade;
  final String unidade;
  final String turma;
  final DateTime liberadoEm;
  final DateTime? validoAte;
  final DateTime? retiradoEm;

  /// Do cache, um liberado pode ter vencido desde o download: a validade vale também offline.
  SituacaoBeneficio situacao([DateTime? agora]) {
    final hoje = DateUtils.dateOnly(agora ?? DateTime.now());
    final venceu = validoAte != null && validoAte!.isBefore(hoje);
    return situacaoNoServidor == SituacaoBeneficio.liberado && venceu ? SituacaoBeneficio.vencido : situacaoNoServidor;
  }

  bool get paraRetirar => situacao() == SituacaoBeneficio.liberado;

  /// Lista da API (ou do cache): os que estão para retirar primeiro, depois o histórico.
  static List<Beneficio> lista(Object? json) {
    final itens = [for (final item in json as List<dynamic>) Beneficio.fromJson(item as Map<String, dynamic>)];
    final paraRetirar = itens.where((b) => b.paraRetirar);
    return [...paraRetirar, ...itens.where((b) => !b.paraRetirar)];
  }

  factory Beneficio.fromJson(Map<String, dynamic> json) {
    final validoAte = json['valid_until'] as String?;
    final retiradoEm = json['redeemed_at'] as String?;
    return Beneficio(
      id: json['id'] as String,
      codigo: json['code'] as String,
      conteudoQr: json['qr_payload'] as String,
      situacaoNoServidor: SituacaoBeneficio.de(json['status'] as String),
      item: json['item_name'] as String,
      tipo: TipoBeneficio.de(json['item_kind'] as String?),
      quantidade: json['quantity'] as int,
      unidade: json['unit'] as String? ?? 'unidade',
      turma: json['class_offering_name'] as String? ?? '',
      liberadoEm: DateTime.parse(json['released_at'] as String),
      validoAte: validoAte == null ? null : lerDia(validoAte),
      retiradoEm: retiradoEm == null ? null : DateTime.parse(retiradoEm),
    );
  }
}
