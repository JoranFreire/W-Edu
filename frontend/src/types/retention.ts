import type { PersonSummary } from '@/types/academicGroups';

export type RiskLevel = 'ok' | 'attention' | 'exceeded';

export interface RetentionRow {
  class_enrollment_id: number;
  student: PersonSummary;
  status: 'active' | 'cancelled' | 'completed';
  sessions: number;
  absences: number;
  absence_percent: number;
  trailing_absences: number;
  level: RiskLevel;
  dismissed_at: string | null;
  dismissal_reason: string | null;
}

export interface RetentionReport {
  class_offering_id: number;
  offering_name: string;
  max_absence_percent: number | null;
  rows: RetentionRow[];
}
