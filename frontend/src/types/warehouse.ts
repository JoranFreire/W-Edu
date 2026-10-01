import type { PersonSummary } from '@/types/academicGroups';

export type MaterialKind = 'consumable' | 'durable';
export type DeliveryMethod = 'qr' | 'manual';
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
  /** Aprovado e ainda nao retirado; livre para aprovar = available - reserved. */
  reserved: number;
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
  delivered_by_name: string | null;
  delivery_method: DeliveryMethod | null;
  delivery_note: string | null;
  /** So para quem pediu, enquanto aprovada: o QR mostrado na retirada. */
  pickup_code: string | null;
  qr_payload: string | null;
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

export interface ItemMovement {
  occurred_at: string;
  kind: 'entry' | 'delivery' | 'return' | 'loss';
  quantity: number;
  person: string | null;
  detail: string | null;
  request_id: string | null;
  method: DeliveryMethod | null;
}
