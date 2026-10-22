export type NotificationChannel = 'internal' | 'whatsapp' | 'email' | 'push';
export type NotificationStatus = 'pending' | 'sent' | 'failed';
export type NotificationEventType =
  | 'class_created'
  | 'meeting_created'
  | 'meeting_reminder'
  | 'absence_registered'
  | 'attendance_recorded'
  | 'content_published'
  | 'certificate_issued'
  | 'grades_published'
  | 'occurrence_registered'
  | 'agenda_published'
  | 'waitlist_promoted'
  | 'activity_reviewed'
  | 'admission_called'
  | 'absence_dismissal'
  | 'material_request_decided'
  | 'gate_passage';

export interface NotificationTemplate {
  id: string;
  key: string;
  channel: NotificationChannel;
  title_template: string;
  body_template: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationTemplateInput {
  key: string;
  channel: NotificationChannel;
  title_template: string;
  body_template: string;
  is_active: boolean;
}

export interface NotificationEvent {
  id: string;
  event_type: NotificationEventType;
  channel: NotificationChannel;
  template_key: string | null;
  recipient_student_id: string | null;
  course_id: string | null;
  class_offering_id: string | null;
  scheduled_meeting_id: string | null;
  payload: Record<string, string>;
  title: string;
  body: string;
  status: NotificationStatus;
  scheduled_for: string | null;
  sent_at: string | null;
  error_message: string | null;
  created_at: string;
}

/** Aviso na caixa do usuario (comunicados internos enderecados a ele). */
export interface InboxNotice {
  id: string;
  event_type: NotificationEventType;
  title: string;
  body: string;
  payload: Record<string, string>;
  read_at: string | null;
  created_at: string;
}

export interface InboxSummary {
  unread: number;
}
