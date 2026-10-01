import type { PersonSummary } from '@/types/academicGroups';
import type { ChargeStatus, PaymentMethod } from '@/types/finance';

export type TuitionBasis = 'program' | 'class_group' | 'credit';
export type DiscountKind = 'scholarship' | 'sibling' | 'punctuality' | 'agreement' | 'other';

export interface TuitionPlan {
  id: string;
  name: string;
  basis: TuitionBasis;
  term_id: string;
  term_name: string;
  program_id: string | null;
  program_name: string | null;
  class_group_id: string | null;
  class_group_name: string | null;
  amount_cents: number;
  installments: number;
  first_due_on: string;
  is_active: boolean;
}

export interface TuitionPlanInput {
  name: string;
  basis: TuitionBasis;
  term_id: string;
  program_id: string | null;
  class_group_id: string | null;
  amount_cents: number;
  installments: number;
  first_due_on: string;
}

export interface GenerationResult {
  enrollments: number;
  created: number;
  skipped: number;
}

export interface Discount {
  id: string;
  program_enrollment_id: string;
  kind: DiscountKind;
  percent: number | null;
  amount_cents: number | null;
  description: string | null;
  valid_from: string;
  valid_until: string | null;
  is_active: boolean;
}

export interface DiscountInput {
  kind: DiscountKind;
  percent: number | null;
  amount_cents: number | null;
  description: string | null;
  valid_from: string;
  valid_until: string | null;
}

export interface LateFeeSettings {
  fine_percent: number;
  monthly_interest_percent: number;
}

export interface Settlement {
  on: string;
  base_cents: number;
  punctuality_discount_cents: number;
  fine_cents: number;
  interest_cents: number;
  total_cents: number;
}

export interface TuitionCharge {
  id: string;
  student: PersonSummary | null;
  payer: PersonSummary | null;
  program_enrollment_id: string | null;
  tuition_plan_id: string | null;
  installment_number: number | null;
  description: string | null;
  due_on: string | null;
  status: ChargeStatus;
  gross_amount_cents: number | null;
  discount_cents: number;
  punctuality_discount_cents: number;
  amount_cents: number;
  fine_cents: number;
  interest_cents: number;
  amount_paid_cents: number | null;
  paid_at: string | null;
  quote: Settlement | null;
}

export interface SettleInput {
  paid_on: string | null;
  payment_method: PaymentMethod;
}
