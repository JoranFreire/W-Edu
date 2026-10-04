import '../../../core/format/dates.dart';
import '../../../core/theme/app_colors.dart';

/// Tipos de item da agenda da turma, com os nomes e as cores do site.
enum TipoAgenda {
  tarefa('homework', 'Tarefa', BadgeCor.azul),
  prova('test', 'Prova', BadgeCor.vermelho),
  evento('event', 'Evento', BadgeCor.roxo),
  aviso('notice', 'Aviso', BadgeCor.amarelo);

  const TipoAgenda(this.valor, this.nome, this.cor);
  final String valor;
  final String nome;
  final BadgeCor cor;

  static TipoAgenda de(String valor) => values.firstWhere((tipo) => tipo.valor == valor, orElse: () => aviso);
}

/// Tarefa, prova, evento ou aviso publicado na agenda da turma.
class ItemAgenda {
  const ItemAgenda({
    required this.id,
    required this.tipo,
    required this.titulo,
    required this.data,
    required this.turma,
    this.descricao,
    this.disciplina,
  });

  final String id;
  final TipoAgenda tipo;
  final String titulo;
  final DateTime data;
  final String turma;
  final String? descricao;
  final String? disciplina;

  /// Lista da API (ou do cache), em ordem de data.
  static List<ItemAgenda> lista(Object? json) =>
      [for (final item in json as List<dynamic>) ItemAgenda.fromJson(item as Map<String, dynamic>)]
        ..sort((a, b) => a.data.compareTo(b.data));

  factory ItemAgenda.fromJson(Map<String, dynamic> json) => ItemAgenda(
        id: json['id'] as String,
        tipo: TipoAgenda.de(json['kind'] as String),
        titulo: json['title'] as String,
        data: lerDia(json['due_on'] as String),
        turma: json['class_group_name'] as String,
        descricao: json['description'] as String?,
        disciplina: json['class_offering_name'] as String?,
      );
}
