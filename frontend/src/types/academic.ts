export type AcademicUnitKind = 'segment' | 'faculty' | 'department' | 'axis' | 'other';
export type ProgramLevel = 'basic' | 'technical' | 'undergraduate' | 'graduate' | 'free';
export type ProgramStatus = 'draft' | 'active' | 'inactive';
export type CurriculumStatus = 'draft' | 'active' | 'archived';
export type ComponentKind = 'mandatory' | 'elective' | 'optional';

export interface AcademicUnit {
  id: number;
  name: string;
  kind: AcademicUnitKind;
  parent_id: number | null;
  is_active: boolean;
}

export interface Program {
  id: number;
  code: string;
  name: string;
  level: ProgramLevel;
  unit_id: number | null;
  degree: string | null;
  duration_terms: number | null;
  total_hours: number | null;
  total_credits: number | null;
  status: ProgramStatus;
}

export interface Subject {
  id: number;
  code: string;
  name: string;
  syllabus: string | null;
  hours: number;
  credits: number | null;
  course_id: number | null;
  is_active: boolean;
}

export interface SubjectSummary {
  id: number;
  code: string;
  name: string;
}

export interface Curriculum {
  id: number;
  program_id: number;
  version: string;
  valid_from: string | null;
  status: CurriculumStatus;
  notes: string | null;
}

export interface CurriculumComponent {
  id: number;
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
