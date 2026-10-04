import 'package:intl/intl.dart';

/// Datas e números no idioma do app (`Intl.defaultLocale`, definido pelo `WEduApp`).

/// Dia (pt-BR `03/10/2026`, en `10/3/2026`).
String formatDay(DateTime date) => DateFormat.yMd().format(date);

String formatDayTime(DateTime date) => DateFormat.yMd().add_Hm().format(date.toLocal());

/// Dia por extenso (pt-BR "sexta-feira, 3 de outubro") — para agrupar a agenda por dia.
String formatLongDay(DateTime date) => DateFormat.MMMMEEEEd().format(date);

/// Lê uma data sem hora (`yyyy-MM-dd`) como dia local, sem deslocar pelo fuso.
DateTime parseDay(String value) {
  final parts = value.split('-').map(int.parse).toList();
  return DateTime(parts[0], parts[1], parts[2]);
}

/// Frações da API (0.85) como porcentagem ("85%").
String formatPercent(double fraction) => NumberFormat.percentPattern().format(fraction);

/// Notas com uma casa (pt-BR "7,5").
String formatGrade(double grade) => NumberFormat('0.0').format(grade);
