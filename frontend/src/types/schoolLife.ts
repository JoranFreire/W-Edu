import type { PersonSummary } from '@/types/academicGroups';

export type OccurrenceKind = 'behavior' | 'lateness' | 'material' | 'health' | 'merit' | 'other';
export type OccurrenceSeverity = 'low' | 'medium' | 'high';
export type AgendaItemKind = 'homework' | 'test' | 'event' | 'notice';

export interface Occurrence {
  id: number;
  student: PersonSummary;
  class_group_id: number | null;
  kind: OccurrenceKind;
  severity: OccurrenceSeverity;
  description: string;
  occurred_on: string;
  reported_by: PersonSummary | null;
  acknowledged_at: string | null;
  created_at: string;
}

export interface OccurrenceInput {
  student_id: number;
  class_group_id: number | null;
  kind: OccurrenceKind;
  severity: OccurrenceSeverity;
  description: string;
  occurred_on: string;
}

export interface AgendaItem {
  id: number;
  class_group_id: number;
  class_group_name: string;
  class_offering_id: number | null;
  class_offering_name: string | null;
  kind: AgendaItemKind;
  title: string;
  description: string | null;
  due_on: string;
  created_at: string;
}

export interface AgendaItemInput {
  kind: AgendaItemKind;
  title: string;
  description: string | null;
  due_on: string;
  class_offering_id: number | null;
}
