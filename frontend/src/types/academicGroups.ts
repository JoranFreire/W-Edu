export type ProgramEnrollmentStatus = 'active' | 'locked' | 'graduated' | 'dropped' | 'transferred' | 'cancelled';
export type Shift = 'morning' | 'afternoon' | 'evening' | 'full_time';

export interface PersonSummary {
  id: string;
  name: string;
  email: string;
}

export interface ProgramEnrollment {
  id: string;
  registration_number: string;
  status: ProgramEnrollmentStatus;
  enrolled_on: string;
  status_changed_at: string;
  curriculum_id: string;
  entry_term_id: string | null;
  concluded_on?: string | null;
  ceremony_on?: string | null;
  student: PersonSummary;
  program: { id: string; code: string; name: string };
}

export interface ClassGroup {
  id: string;
  program_id: string;
  term_id: string;
  name: string;
  curriculum_term_number: number | null;
  shift: Shift;
  capacity: number | null;
  homeroom_teacher_id: string | null;
  member_count: number;
}

export interface ClassGroupMember {
  id: string;
  program_enrollment_id: string;
  registration_number: string;
  student: PersonSummary;
}
