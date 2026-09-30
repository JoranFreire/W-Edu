import type { ComponentKind } from '@/types/academic';

export type EnrollmentEventKind =
  | 'enrolled' | 'reenrolled' | 'locked' | 'reactivated' | 'cancelled' | 'dropped'
  | 'transferred_out' | 'transferred_internal' | 'curriculum_changed' | 'graduated';
export type CreditTransferOrigin = 'internal' | 'external';
export type CreditTransferStatus = 'requested' | 'approved' | 'rejected';
export type TranscriptStatus = 'completed' | 'credited' | 'in_progress' | 'failed' | 'pending';

export interface EnrollmentEvent {
  id: number;
  kind: EnrollmentEventKind;
  term_id: number | null;
  reason: string | null;
  details: Record<string, unknown>;
  created_by_id: number | null;
  created_at: string;
}

export interface TermRegistration {
  id: number;
  term_id: number;
  term_name: string;
  curriculum_term_number: number | null;
  registered_at: string;
}

export interface CreditTransfer {
  id: number;
  subject_id: number;
  subject_code: string;
  subject_name: string;
  origin: CreditTransferOrigin;
  source_institution: string | null;
  source_subject: string;
  grade: number | null;
  hours: number | null;
  status: CreditTransferStatus;
  decision_note: string | null;
  decided_at: string | null;
  created_at: string;
}

export interface TranscriptRow {
  subject_id: number;
  code: string;
  name: string;
  term_number: number;
  kind: ComponentKind;
  hours: number;
  credits: number | null;
  status: TranscriptStatus;
  grade: number | null;
  taken_in: string | null;
  attempts: number;
}

export interface Transcript {
  program_enrollment_id: number;
  registration_number: string;
  student_name: string;
  program_code: string;
  program_name: string;
  curriculum_version: string;
  status: string;
  rows: TranscriptRow[];
  summary: {
    cr: number | null;
    mandatory_hours: number;
    mandatory_hours_done: number;
    elective_hours_done: number;
    hours_done: number;
    integralization: number;
    completed_components: number;
    total_components: number;
  };
}
