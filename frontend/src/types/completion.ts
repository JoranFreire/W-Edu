import type { PersonSummary } from '@/types/academicGroups';

export type ActivityCategory = 'teaching' | 'research' | 'extension' | 'cultural' | 'professional' | 'other';
export type ReviewStatus = 'submitted' | 'approved' | 'rejected';
export type InternshipStatus = 'in_progress' | 'completed' | 'cancelled';
export type FinalProjectStatus = 'in_progress' | 'submitted' | 'approved' | 'failed';

export interface Requirement {
  key: 'mandatory_hours' | 'total_hours' | 'credits' | 'complementary_hours' | 'internship_hours' | 'final_project';
  label: string;
  done: number;
  required: number;
  unit: string;
  met: boolean;
}

export interface Integralization {
  program_enrollment_id: number;
  registration_number: string;
  program_name: string;
  cr: number | null;
  requirements: Requirement[];
  complete: boolean;
}

export interface Activity {
  id: number;
  program_enrollment_id: number;
  category: ActivityCategory;
  title: string;
  description: string | null;
  occurred_on: string;
  hours_requested: number;
  hours_approved: number | null;
  status: ReviewStatus;
  decision_note: string | null;
  decided_at: string | null;
  created_at: string;
}

export interface ActivityInput {
  category: ActivityCategory;
  title: string;
  description: string | null;
  occurred_on: string;
  hours_requested: number;
}

export interface ActivityDecisionInput {
  approved: boolean;
  hours_approved: number | null;
  note: string | null;
}

export interface Internship {
  id: number;
  program_enrollment_id: number;
  student: PersonSummary;
  company_name: string;
  supervisor_name: string | null;
  advisor: PersonSummary | null;
  is_mandatory: boolean;
  agreement_number: string | null;
  starts_on: string;
  ends_on: string | null;
  planned_hours: number | null;
  status: InternshipStatus;
  notes: string | null;
  approved_hours: number;
  pending_hours: number;
}

export interface InternshipInput {
  company_name: string;
  supervisor_name: string | null;
  advisor_id: number | null;
  is_mandatory: boolean;
  agreement_number: string | null;
  starts_on: string;
  ends_on: string | null;
  planned_hours: number | null;
}

export interface InternshipLog {
  id: number;
  internship_id: number;
  worked_on: string;
  hours: number;
  activities: string;
  status: ReviewStatus;
  reviewed_at: string | null;
}

export interface InternshipLogInput {
  worked_on: string;
  hours: number;
  activities: string;
}

export interface FinalProject {
  id: number;
  program_enrollment_id: number;
  student: PersonSummary;
  title: string;
  advisor: PersonSummary | null;
  co_advisor_name: string | null;
  status: FinalProjectStatus;
  defense_on: string | null;
  grade: number | null;
  committee: string | null;
  notes: string | null;
}

export interface FinalProjectInput {
  title: string;
  advisor_id: number | null;
  co_advisor_name: string | null;
  notes: string | null;
}

export interface FinalProjectResultInput {
  status: 'submitted' | 'approved' | 'failed';
  defense_on: string | null;
  grade: number | null;
  committee: string | null;
}

export interface Advising {
  internships: Internship[];
  final_projects: FinalProject[];
}
