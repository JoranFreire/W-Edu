import type { BenefitKind } from '@/types/socialPrograms';

export type VoucherStatus = 'released' | 'redeemed' | 'cancelled' | 'expired';

/** Beneficio liberado para retirada com QR. */
export interface BenefitVoucher {
  id: string;
  code: string;
  qr_payload: string;
  status: VoucherStatus;
  item_id: string;
  item_name: string;
  item_kind: BenefitKind;
  unit: string;
  quantity: number;
  student: { id: string; name: string; email: string };
  class_offering_id: string;
  class_offering_name: string;
  scheduled_meeting_id: string | null;
  valid_until: string | null;
  released_at: string;
  redeemed_at: string | null;
}

export interface VoucherBatchResult {
  released: number;
  available_stock: number;
}
