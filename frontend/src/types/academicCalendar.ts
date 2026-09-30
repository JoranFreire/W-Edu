export type TermKind = 'year' | 'semester' | 'quarter' | 'module';
export type TermStatus = 'planned' | 'open' | 'closed';
export type GradingPeriodStatus = 'open' | 'closed';
export type CalendarEventKind = 'school_day' | 'holiday' | 'recess' | 'exam' | 'event';

export interface AcademicTerm {
  id: number;
  name: string;
  kind: TermKind;
  starts_on: string;
  ends_on: string;
  status: TermStatus;
}

export interface GradingPeriod {
  id: number;
  term_id: number;
  name: string;
  order: number;
  starts_on: string;
  ends_on: string;
  weight: number;
  status: GradingPeriodStatus;
}

export interface CalendarEvent {
  id: number;
  term_id: number | null;
  kind: CalendarEventKind;
  title: string;
  starts_on: string;
  ends_on: string | null;
}

export interface TermCalendarSummary {
  school_days: number;
  non_school_days: number;
  extra_school_days: number;
  exams: number;
}
