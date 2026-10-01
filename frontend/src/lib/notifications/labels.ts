import type { NotificationChannel, NotificationEventType, NotificationStatus } from '@/types/notification';

export const notificationEventLabels: Record<NotificationEventType, string> = {
  class_created: 'Nova turma criada',
  meeting_created: 'Encontro agendado',
  meeting_reminder: 'Lembrete de encontro',
  absence_registered: 'Falta registrada',
  attendance_recorded: 'Presença registrada',
  content_published: 'Novo conteúdo publicado',
  certificate_issued: 'Certificado emitido',
  grades_published: 'Resultado final publicado',
  occurrence_registered: 'Ocorrência registrada',
  agenda_published: 'Agenda da turma',
  waitlist_promoted: 'Vaga confirmada (lista de espera)',
  activity_reviewed: 'Atividade complementar avaliada',
  admission_called: 'Convocação do edital',
  absence_dismissal: 'Desligamento por faltas',
  material_request_decided: 'Requisição de material decidida',
};

export const notificationChannelLabels: Record<NotificationChannel, string> = {
  internal: 'Interno',
  whatsapp: 'WhatsApp',
  email: 'E-mail',
  push: 'Push',
};

export const notificationStatusLabels: Record<NotificationStatus, string> = {
  pending: 'Pendente',
  sent: 'Enviado',
  failed: 'Falhou',
};

/** Nome de negocio do evento; chaves desconhecidas (templates personalizados) aparecem como vieram. */
export function notificationEventLabel(key: string): string {
  return notificationEventLabels[key as NotificationEventType] ?? key;
}
