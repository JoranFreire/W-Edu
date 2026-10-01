export type AcademicUnitKind = 'segment' | 'faculty' | 'department' | 'axis' | 'other';
export type ProgramLevel = 'basic' | 'technical' | 'undergraduate' | 'graduate' | 'free';
export type ProgramStatus = 'draft' | 'active' | 'inactive';
export type CurriculumStatus = 'draft' | 'active' | 'archived';
export type ComponentKind = 'mandatory' | 'elective' | 'optional';

export interface AcademicUnit {
  id: string;
  name: string;
  kind: AcademicUnitKind;
  parent_id: string | null;
  is_active: boolean;
}

export interface Program {
  id: string;
  code: string;
  name: string;
  level: ProgramLevel;
  unit_id: string | null;
  degree: string | null;
  duration_terms: number | null;
  total_hours: number | null;
  total_credits: number | null;
  complementary_hours: number | null;
  internship_hours: number | null;
  requires_final_project: boolean;
  status: ProgramStatus;
}

export interface Subject {
  id: string;
  code: string;
  name: string;
  syllabus: string | null;
  hours: number;
  credits: number | null;
  course_id: string | null;
  is_active: boolean;
}

export interface SubjectSummary {
  id: string;
  code: string;
  name: string;
}

export interface Curriculum {
  id: string;
  program_id: string;
  version: string;
  valid_from: string | null;
  status: CurriculumStatus;
  notes: string | null;
}

export interface CurriculumComponent {
  id: string;
  subject: SubjectSummary;
  term_number: number;
  kind: ComponentKind;
  hours: number;
  credits: number | null;
  hours_override: number | null;
  credits_override: number | null;
}

export interface CurriculumDetail extends Curriculum {
  components: CurriculumComponent[];
  totals: { hours: number; credits: number; mandatory_hours: number; terms: number };
  issues: string[];
}
