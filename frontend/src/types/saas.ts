export type SaasSubscriptionStatus = 'trial' | 'active' | 'past_due' | 'cancelled';
export type PlatformInvoiceStatus = 'pending' | 'paid' | 'cancelled';

export interface SaasPlan {
  id: number;
  name: string;
  description: string | null;
  monthly_price_cents: number;
  max_students: number | null;
  is_active: boolean;
}

export interface SaasPlanInput {
  name: string;
  description: string | null;
  monthly_price_cents: number;
  max_students: number | null;
}

export interface InstitutionSubscription {
  institution_id: number;
  plan: SaasPlan;
  status: SaasSubscriptionStatus;
  started_on: string;
  trial_ends_on: string | null;
}

export interface SubscriptionInput {
  plan_id: number;
  status: SaasSubscriptionStatus;
  trial_ends_on: string | null;
}

export interface PlatformInvoice {
  id: number;
  institution_id: number;
  plan_name: string;
  period_start: string;
  period_end: string;
  amount_cents: number;
  due_on: string;
  status: PlatformInvoiceStatus;
  paid_at: string | null;
}

export interface InstitutionPlan {
  subscription: InstitutionSubscription | null;
  usage: { active_students: number; max_students: number | null };
  invoices: PlatformInvoice[];
}
