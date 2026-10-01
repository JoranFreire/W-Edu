import 'package:intl/intl.dart';

/// Datas no formato brasileiro, iguais às do site.
final _dia = DateFormat('dd/MM/yyyy', 'pt_BR');
final _diaHora = DateFormat("dd/MM/yyyy 'às' HH:mm", 'pt_BR');
final _diaSemana = DateFormat("EEEE, d 'de' MMMM", 'pt_BR');

/// `2026-10-03` (data sem hora, como a API manda prazos) → `03/10/2026`.
String formatarDia(DateTime data) => _dia.format(data);

String formatarDiaHora(DateTime data) => _diaHora.format(data.toLocal());

/// "sexta-feira, 3 de outubro" — para agrupar a agenda por dia.
String formatarDiaPorExtenso(DateTime data) => _diaSemana.format(data);

/// Lê uma data sem hora (`yyyy-MM-dd`) como dia local, sem deslocar pelo fuso.
DateTime lerDia(String valor) {
  final partes = valor.split('-').map(int.parse).toList();
  return DateTime(partes[0], partes[1], partes[2]);
}

/// Frações da API (0.85) como porcentagem ("85%").
String formatarPorcentagem(double fracao) => '${(fracao * 100).round()}%';

/// Notas com uma casa e vírgula ("7,5").
String formatarNota(double nota) => nota.toStringAsFixed(1).replaceAll('.', ',');
