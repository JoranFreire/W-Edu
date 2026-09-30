from app.models.notification import NotificationChannel, NotificationEventType

# Template padrao de cada evento no canal interno; criado sob demanda em cada instituicao.
DEFAULT_TEMPLATES = {
    (NotificationEventType.class_created, NotificationChannel.internal): (
        "Nova turma criada",
        "A turma {class_name} do curso {course_name} foi criada.",
    ),
    (NotificationEventType.meeting_created, NotificationChannel.internal): (
        "Encontro agendado",
        "O encontro {meeting_title} foi agendado para {starts_at}.",
    ),
    (NotificationEventType.absence_registered, NotificationChannel.internal): (
        "Falta registrada",
        "O aluno {student_name} recebeu falta no encontro {meeting_title}.",
    ),
    (NotificationEventType.attendance_recorded, NotificationChannel.internal): (
        "Presença registrada",
        "A presença do aluno {student_name} foi registrada no encontro {meeting_title}.",
    ),
    (NotificationEventType.certificate_issued, NotificationChannel.internal): (
        "Certificado emitido",
        "O certificado do curso {course_name} foi emitido para {student_name}.",
    ),
    (NotificationEventType.content_published, NotificationChannel.internal): (
        "Novo conteúdo publicado",
        "A aula {lesson_title} foi publicada no curso {course_name}.",
    ),
    (NotificationEventType.grades_published, NotificationChannel.internal): (
        "Boletim disponível",
        "O resultado final de {class_name} foi publicado: {result_label}.",
    ),
    (NotificationEventType.meeting_reminder, NotificationChannel.internal): (
        "Lembrete de encontro",
        "Você tem um encontro em {starts_at}: {meeting_title}.",
    ),
}
