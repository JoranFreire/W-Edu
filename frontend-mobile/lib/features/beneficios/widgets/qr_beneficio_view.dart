import 'package:flutter/material.dart';

import '../../../core/format/datas.dart';
import '../../../shared/ds/ds.dart';
import '../data/beneficio.dart';

/// O QR de retirada de um benefício (item, tipo, turma e validade).
Future<void> abrirQrDoBeneficio(BuildContext context, Beneficio beneficio) {
  final validade = beneficio.validoAte == null ? 'Sem data de validade' : 'Válido até ${formatarDia(beneficio.validoAte!)}';
  return QrRetirada(
    icone: beneficio.tipo.icone,
    titulo: '${beneficio.item} × ${beneficio.quantidade} ${beneficio.unidade}',
    subtitulo: [beneficio.tipo.nome, if (beneficio.turma.isNotEmpty) beneficio.turma].join(' · '),
    conteudo: beneficio.conteudoQr,
    codigo: beneficio.codigo,
    rodape: '$validade\nMostre este QR na retirada.',
  ).abrir(context);
}
