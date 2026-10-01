import type { PersonSummary } from '@/types/academicGroups';

export type MaterialKind = 'consumable' | 'durable';
export type RequestStatus = 'pending' | 'approved' | 'rejected' | 'delivered' | 'closed' | 'cancelled';

export interface WarehouseItem {
  id: string;
  name: string;
  category: string | null;
  kind: MaterialKind;
  unit: string;
  min_stock: number;
  location: string | null;
  unit_cost_cents: number;
  is_active: boolean;
  available: number;
  on_loan: number;
  below_minimum: boolean;
}

export interface WarehouseItemInput {
  name: string;
  category: string | null;
  kind: MaterialKind;
  unit: string;
  min_stock: number;
  location: string | null;
  unit_cost_cents: number;
}

export interface EntryInput {
  quantity: number;
  unit_cost_cents: number | null;
  origin: 'purchase' | 'donation';
  funding_source_id: string | null;
  received_on: string;
}

export interface RequestLine {
  id: string;
  item_id: string;
  item_name: string;
  kind: MaterialKind;
  unit: string;
  quantity_requested: number;
  quantity_approved: number | null;
  quantity_delivered: number;
  quantity_returned: number;
  quantity_lost: number;
  outstanding: number;
}

export interface MaterialRequest {
  id: string;
  requester: PersonSummary;
  class_offering_id: string | null;
  class_offering_name: string | null;
  purpose: string;
  needed_on: string;
  status: RequestStatus;
  decision_note: string | null;
  decided_at: string | null;
  delivered_at: string | null;
  return_due_on: string | null;
  overdue: boolean;
  created_at: string;
  lines: RequestLine[];
}

export interface MaterialRequestInput {
  purpose: string;
  needed_on: string;
  class_offering_id: string | null;
  lines: { item_id: string; quantity: number }[];
}

export interface ConsumptionRow {
  label: string;
  quantity: number;
  cost_cents: number;
}

export interface Consumption {
  by_item: ConsumptionRow[];
  by_requester: ConsumptionRow[];
  by_offering: ConsumptionRow[];
  total_cost_cents: number;
}
