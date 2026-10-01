import type { PersonSummary } from '@/types/academicGroups';

export type GuardianRelationship = 'mother' | 'father' | 'legal_guardian' | 'grandparent' | 'other';

export interface GuardianLink {
  id: string;
  student: PersonSummary;
  guardian: PersonSummary;
  relationship_kind: GuardianRelationship;
  is_financial: boolean;
  can_pick_up: boolean;
  is_primary: boolean;
}

export interface Dependent {
  link_id: string;
  student: PersonSummary;
  relationship_kind: GuardianRelationship;
  is_financial: boolean;
  can_pick_up: boolean;
}

export interface DependentNotice {
  id: string;
  title: string;
  body: string;
  created_at: string;
}

export interface DependentCharge {
  id: string;
  amount_cents: number;
  currency: string;
  status: string;
  due_at: string | null;
  checkout_url: string | null;
  bank_slip_url: string | null;
}
