export type BillingPeriod = 'one_time' | 'monthly' | 'quarterly' | 'yearly';
export type SubscriptionStatus = 'active' | 'paused' | 'cancelled' | 'overdue' | 'completed';
export type PaymentMethod = 'pix' | 'card' | 'boleto' | 'manual';
export type ChargeStatus = 'pending' | 'paid' | 'failed' | 'cancelled' | 'refunded';

export interface BillingPlan {
  id: string;
  name: string;
  description: string | null;
  price_cents: number;
  currency: string;
  billing_period: BillingPeriod;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: string;
  billing_plan_id: string;
  student_id: string | null;
  organization_id: string | null;
  status: SubscriptionStatus;
  start_date: string;
  current_period_start: string;
  current_period_end: string;
  next_billing_at: string | null;
  gateway_name: string | null;
  gateway_customer_id: string | null;
  created_at: string;
}

export interface Charge {
  id: string;
  billing_plan_id: string | null;
  subscription_id: string | null;
  student_id: string | null;
  organization_id: string | null;
  course_id: string | null;
  class_offering_id: string | null;
  amount_cents: number;
  currency: string;
  payment_method: PaymentMethod;
  status: ChargeStatus;
  gateway_name: string | null;
  gateway_customer_id: string | null;
  gateway_reference: string | null;
  gateway_status: string | null;
  checkout_url: string | null;
  bank_slip_url: string | null;
  pix_qr_code_payload: string | null;
  pix_qr_code_image: string | null;
  due_at: string | null;
  paid_at: string | null;
  description: string | null;
  created_at: string;
}
