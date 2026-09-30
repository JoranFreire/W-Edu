export type ProgramEnrollmentStatus = 'active' | 'locked' | 'graduated' | 'dropped' | 'transferred' | 'cancelled';
export type Shift = 'morning' | 'afternoon' | 'evening' | 'full_time';

export interface PersonSummary {
  id: number;
  name: string;
  email: string;
}

export interface ProgramEnrollment {
  id: number;
  registration_number: string;
  status: ProgramEnrollmentStatus;
  enrolled_on: string;
  status_changed_at: string;
  curriculum_id: number;
  entry_term_id: number | null;
  student: PersonSummary;
  program: { id: number; code: string; name: string };
}

export interface ClassGroup {
  id: number;
  program_id: number;
  term_id: number;
  name: string;
  curriculum_term_number: number | null;
  shift: Shift;
  capacity: number | null;
  homeroom_teacher_id: number | null;
  member_count: number;
}

export interface ClassGroupMember {
  id: number;
  program_enrollment_id: number;
  registration_number: string;
  student: PersonSummary;
}
