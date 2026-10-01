import type { PersonSummary } from '@/types/academicGroups';

export type FundingKind = 'agreement' | 'government' | 'system_s' | 'parliamentary' | 'donation' | 'own' | 'other';
export type BenefitKind = 'snack' | 'material' | 'uniform' | 'transport' | 'stipend' | 'other';
export type StockOrigin = 'purchase' | 'donation';

export interface FundingSource {
  id: string;
  name: string;
  kind: FundingKind;
  agreement_number: string | null;
  amount_cents: number | null;
  starts_on: string;
  ends_on: string | null;
  notes: string | null;
  is_active: boolean;
}

export type FundingSourceInput = Omit<FundingSource, 'id' | 'is_active'>;

export interface BenefitItem {
  id: string;
  name: string;
  kind: BenefitKind;
  unit: string;
  unit_cost_cents: number;
  requires_attendance: boolean;
  is_active: boolean;
  stock: number;
  /** Liberado em QR e ainda nao retirado; disponivel = stock - reserved. */
  reserved: number;
}

export type BenefitItemInput = Pick<BenefitItem, 'name' | 'kind' | 'unit' | 'unit_cost_cents' | 'requires_attendance'>;

export interface StockEntryInput {
  quantity: number;
  unit_cost_cents: number | null;
  origin: StockOrigin;
  funding_source_id: string | null;
  received_on: string;
}

export interface Delivery {
  id: string;
  item_id: string;
  item_name: string;
  student: PersonSummary;
  class_offering_id: string;
  scheduled_meeting_id: string | null;
  quantity: number;
  unit_cost_cents: number;
  delivered_on: string;
}

export interface OfferingIndicators {
  class_offering_id: string | null;
  name: string;
  applications: number;
  enrolled: number;
  active: number;
  completed: number;
  dismissed: number;
  dropped: number;
  evasion_rate: number;
}

export interface FundingReport {
  funding: FundingSource;
  offerings: OfferingIndicators[];
  totals: OfferingIndicators;
  profile: {
    respondents: number;
    age: Record<string, number>;
    income_per_capita: Record<string, number>;
    schooling: Record<string, number>;
    reserved_seats: number;
  };
  benefits: { item_name: string; unit: string; quantity: number; cost_cents: number }[];
  stock_received_cents: number;
  benefits_cost_cents: number;
  materials: { item_name: string; unit: string; quantity: number; cost_cents: number }[];
  materials_cost_cents: number;
  budget_balance_cents: number | null;
  minimum_wage_cents: number;
  minimum_wage_source: 'bcb' | 'seed' | 'informed' | 'fallback';
}
