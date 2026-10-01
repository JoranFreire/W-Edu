import type { ProgramEnrollmentStatus } from '@/types/academicGroups';
import type { User } from '@/types/auth';
import type { GuardianRelationship } from '@/types/guardians';
import type { OccurrenceKind, OccurrenceSeverity } from '@/types/schoolLife';
import type { RequestStatus } from '@/types/warehouse';

export interface DossierContact {
  phone: string | null;
  document: string | null;
  position: string | null;
  department: string | null;
  bio: string | null;
}

export interface DossierGuardianLink {
  link_id: string;
  person: { id: string; name: string; email: string; phone: string | null };
  relationship_kind: GuardianRelationship;
  is_financial: boolean;
  is_primary: boolean;
  can_pick_up: boolean;
}

export interface DossierProgramEnrollment {
  id: string;
  program_code: string;
  program_name: string;
  registration_number: string;
  status: ProgramEnrollmentStatus;
  enrolled_on: string;
  entry_term_name: string | null;
}

/** Secoes nulas: quem consulta nao tem a permissao da area (a tela as omite). */
export interface UserDossier {
  user: User;
  organization_name: string | null;
  contact: DossierContact;
  guardians: DossierGuardianLink[] | null;
  dependents: DossierGuardianLink[] | null;
  program_enrollments: DossierProgramEnrollment[] | null;
  courses: DossierCourse[];
  certificates: { id: string; course_name: string; validation_code: string; issued_at: string; revoked: boolean }[];
  finance: DossierFinance | null;
  occurrences: {
    total: number;
    recent: { id: string; kind: OccurrenceKind; severity: OccurrenceSeverity; description: string; occurred_on: string }[];
  } | null;
  benefits: DossierBenefit[] | null;
  materials: DossierMaterialRequest[] | null;
  teaching: { id: string; name: string; course_name: string; term_name: string | null }[] | null;
}

export interface DossierCourse {
  course_id: string;
  course_name: string;
  total_lessons: number;
  done_lessons: number;
  progress_percent: number;
  completed: boolean;
  last_activity_at: string | null;
}

export interface DossierCharge {
  id: string;
  description: string | null;
  amount_cents: number;
  status: 'pending' | 'paid' | 'failed' | 'cancelled' | 'refunded';
  due_at: string | null;
  paid_at: string | null;
  installment_number: number | null;
  /** A pessoa e quem paga (responsavel financeiro), nao o aluno da cobranca. */
  as_payer: boolean;
}

export interface DossierFinance {
  open_count: number;
  overdue_count: number;
  open_cents: number;
  next_due_at: string | null;
  charges: DossierCharge[];
}

export interface DossierBenefit {
  id: string;
  item_name: string;
  unit: string;
  quantity: number;
  delivered_on: string;
  offering_name: string;
}

export interface DossierMaterialRequest {
  id: string;
  purpose: string;
  needed_on: string;
  status: RequestStatus;
  offering_name: string | null;
  return_due_on: string | null;
  lines: { item_name: string; unit: string; requested: number; approved: number | null; delivered: number; returned: number }[];
}
