import '../../../core/format/datas.dart';
import '../../../core/theme/app_colors.dart';

enum SituacaoRequisicao {
  pendente('pending', 'Aguardando aprovação', BadgeCor.amarelo),
  aprovada('approved', 'Aprovada: retirar', BadgeCor.roxo),
  recusada('rejected', 'Recusada', BadgeCor.vermelho),
  retirada('delivered', 'Retirada', BadgeCor.azul),
  concluida('closed', 'Concluída', BadgeCor.verde),
  cancelada('cancelled', 'Cancelada', BadgeCor.cinza);

  const SituacaoRequisicao(this.valor, this.nome, this.cor);
  final String valor;
  final String nome;
  final BadgeCor cor;

  static SituacaoRequisicao de(String valor) => values.firstWhere((s) => s.valor == valor, orElse: () => cancelada);
}

class LinhaRequisicao {
  const LinhaRequisicao({required this.material, required this.unidade, required this.pedido, this.aprovado, required this.retirado, required this.emprestado});

  final String material;
  final String unidade;
  final int pedido;
  final int? aprovado;
  final int retirado;

  /// Permanentes ainda fora do almoxarifado (a devolver).
  final int emprestado;

  /// O que vale agora: retirado, senão aprovado, senão pedido.
  String get resumo {
    final quantidade = retirado > 0 ? retirado : aprovado ?? pedido;
    final devolver = emprestado > 0 ? ' · devolver $emprestado' : '';
    return '$material: $quantidade $unidade$devolver';
  }

  factory LinhaRequisicao.fromJson(Map<String, dynamic> json) => LinhaRequisicao(
        material: json['item_name'] as String,
        unidade: json['unit'] as String,
        pedido: json['quantity_requested'] as int,
        aprovado: json['quantity_approved'] as int?,
        retirado: json['quantity_delivered'] as int,
        emprestado: json['outstanding'] as int,
      );
}

/// Requisição de material ao almoxarifado, de quem pediu: aprovada, traz o QR de retirada.
class Requisicao {
  const Requisicao({
    required this.id,
    required this.finalidade,
    required this.paraDia,
    required this.situacao,
    required this.linhas,
    this.turma,
    this.devolverAte,
    this.atrasada = false,
    this.observacao,
    this.codigoRetirada,
    this.conteudoQr,
  });

  final String id;
  final String finalidade;
  final DateTime paraDia;
  final SituacaoRequisicao situacao;
  final List<LinhaRequisicao> linhas;
  final String? turma;
  final DateTime? devolverAte;
  final bool atrasada;
  final String? observacao;
  final String? codigoRetirada;
  final String? conteudoQr;

  bool get paraRetirar => situacao == SituacaoRequisicao.aprovada && conteudoQr != null;

  /// As aprovadas (para retirar) primeiro; depois na ordem da API (mais recentes).
  static List<Requisicao> lista(Object? json) {
    final itens = [for (final item in json as List<dynamic>) Requisicao.fromJson(item as Map<String, dynamic>)];
    return [...itens.where((r) => r.paraRetirar), ...itens.where((r) => !r.paraRetirar)];
  }

  factory Requisicao.fromJson(Map<String, dynamic> json) {
    final devolver = json['return_due_on'] as String?;
    return Requisicao(
      id: json['id'] as String,
      finalidade: json['purpose'] as String,
      paraDia: lerDia(json['needed_on'] as String),
      situacao: SituacaoRequisicao.de(json['status'] as String),
      linhas: [for (final linha in json['lines'] as List<dynamic>) LinhaRequisicao.fromJson(linha as Map<String, dynamic>)],
      turma: json['class_offering_name'] as String?,
      devolverAte: devolver == null ? null : lerDia(devolver),
      atrasada: json['overdue'] as bool? ?? false,
      observacao: json['decision_note'] as String?,
      codigoRetirada: json['pickup_code'] as String?,
      conteudoQr: json['qr_payload'] as String?,
    );
  }
}
