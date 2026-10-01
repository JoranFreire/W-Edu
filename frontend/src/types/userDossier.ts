import type { ProgramEnrollmentStatus } from '@/types/academicGroups';
import type { User } from '@/types/auth';
import type { GuardianRelationship } from '@/types/guardians';
import type { OccurrenceKind, OccurrenceSeverity } from '@/types/schoolLife';

export interface DossierContact {
  phone: string | null;
  document: string | null;
  position: string | null;
  department: string | null;
  bio: string | null;
}

export interface DossierGuardianLink {
  link_id: number;
  person: { id: number; name: string; email: string; phone: string | null };
  relationship_kind: GuardianRelationship;
  is_financial: boolean;
  is_primary: boolean;
  can_pick_up: boolean;
}

export interface DossierProgramEnrollment {
  id: number;
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
  courses: { course_id: number; course_name: string; enrolled_at: string }[];
  certificates: { id: number; course_name: string; validation_code: string; issued_at: string; revoked: boolean }[];
  finance: { open_count: number; overdue_count: number; open_cents: number; next_due_at: string | null } | null;
  occurrences: {
    total: number;
    recent: { id: number; kind: OccurrenceKind; severity: OccurrenceSeverity; description: string; occurred_on: string }[];
  } | null;
  teaching: { id: number; name: string; course_name: string; term_name: string | null }[] | null;
}
