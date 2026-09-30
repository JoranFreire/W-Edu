import type { PersonSummary } from '@/types/academicGroups';

export type GradingScale = 'numeric' | 'concept';
export type AverageFormula = 'arithmetic' | 'weighted';
export type AssessmentKind = 'test' | 'assignment' | 'quiz' | 'practical' | 'participation';

export interface ConceptBand {
  code: string;
  min_value: number;
}

export interface GradingScheme {
  id: number | null;
  name: string;
  scale: GradingScale;
  min_value: number;
  max_value: number;
  passing_grade: number;
  formula: AverageFormula;
  recovery_enabled: boolean;
  min_attendance: number;
  concepts: ConceptBand[];
  is_default: boolean;
}

export interface TeachingOffering {
  id: number;
  name: string;
  course_id: number;
  instructor_id: number | null;
  term_id: number | null;
  subject_id: number | null;
  class_group_id: number | null;
  grading_scheme_id: number | null;
  starts_at: string;
  ends_at: string;
}

export interface AssessmentItem {
  id: number;
  class_offering_id: number;
  grading_period_id: number | null;
  name: string;
  kind: AssessmentKind;
  weight: number;
  max_score: number;
  quiz_id: number | null;
  due_on: string | null;
}

export interface GradeRow {
  class_enrollment_id: number;
  student: PersonSummary;
  score: number | null;
  notes: string | null;
}

export interface GradebookRow {
  class_enrollment_id: number;
  student: PersonSummary;
  scores: Record<string, number | null>;
  period_averages: Record<string, number | null>;
  average: number | null;
  concept: string | null;
  absences: number;
  attendance_rate: number | null;
}

export interface Gradebook {
  scheme: GradingScheme;
  periods: { id: number | null; name: string; status: string }[];
  items: AssessmentItem[];
  rows: GradebookRow[];
  total_lessons: number;
}

export interface DiaryEntry {
  id: number;
  class_offering_id: number;
  date: string;
  lesson_count: number;
  content_taught: string;
  instructor_id: number | null;
  scheduled_meeting_id: number | null;
  locked: boolean;
}

export interface DiaryAttendanceRow {
  class_enrollment_id: number;
  student: PersonSummary;
  absences: number;
  justified: boolean;
  note: string | null;
}

export type ClassEnrollmentResult = 'in_progress' | 'recovery' | 'approved' | 'failed' | 'failed_attendance';

export interface PeriodResult {
  grading_period_id: number;
  average: number | null;
  absences: number;
}

export interface FinalResultRow {
  class_enrollment_id: number;
  student: PersonSummary;
  periods: PeriodResult[];
  average: number | null;
  recovery_score: number | null;
  final_grade: number | null;
  attendance_rate: number | null;
  result: ClassEnrollmentResult;
}

export interface OfferingResults {
  scheme: GradingScheme;
  closed_period_ids: number[];
  pending_period_ids: number[];
  finalized: boolean;
  rows: FinalResultRow[];
}

export interface ReportCardEntry {
  class_offering_id: number;
  offering_name: string;
  periods: { name: string; average: number | null; absences: number }[];
  final_grade: number | null;
  recovery_score: number | null;
  attendance_rate: number | null;
  result: ClassEnrollmentResult;
  finalized: boolean;
  passing_grade: number;
  min_attendance: number;
}
