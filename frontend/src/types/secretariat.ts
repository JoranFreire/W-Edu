import type { ComponentKind } from '@/types/academic';

export type EnrollmentEventKind =
  | 'enrolled' | 'reenrolled' | 'locked' | 'reactivated' | 'cancelled' | 'dropped'
  | 'transferred_out' | 'transferred_internal' | 'curriculum_changed' | 'graduated';
export type CreditTransferOrigin = 'internal' | 'external';
export type CreditTransferStatus = 'requested' | 'approved' | 'rejected';
export type TranscriptStatus = 'completed' | 'credited' | 'in_progress' | 'failed' | 'pending';

export interface EnrollmentEvent {
  id: string;
  kind: EnrollmentEventKind;
  term_id: string | null;
  reason: string | null;
  details: Record<string, unknown>;
  created_by_id: string | null;
  created_at: string;
}

export interface TermRegistration {
  id: string;
  term_id: string;
  term_name: string;
  curriculum_term_number: number | null;
  registered_at: string;
}

export interface CreditTransfer {
  id: string;
  subject_id: string;
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
  subject_id: string;
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
  program_enrollment_id: string;
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

export type DeclarationKind = 'enrollment' | 'attendance' | 'completion';

export interface Declaration {
  id: string;
  program_enrollment_id: string;
  kind: DeclarationKind;
  term_id: string | null;
  title: string;
  lines: string[];
  validation_code: string;
  issued_at: string;
  revoked_at: string | null;
  revoked_reason: string | null;
}

export interface DeclarationValidation {
  valid: boolean;
  message: string;
  kind: DeclarationKind | null;
  title: string | null;
  student_name: string | null;
  institution_name: string | null;
  issued_at: string | null;
}

export interface ConclusionCheck {
  eligible: boolean;
  status: string;
  integralization: number;
  hours_done: number;
  required_hours: number | null;
  missing: string[];
}
