/// Áreas de dados do backend (`app/services/sync/areas.py`): cada tela pertence a uma.
abstract final class SyncAreas {
  static const notices = 'notifications';
  static const agenda = 'agenda';
  static const reportCard = 'report_card';
  static const dependents = 'dependents';
  static const benefits = 'benefits';
  static const materials = 'materials';
  static const teaching = 'teaching';
}
