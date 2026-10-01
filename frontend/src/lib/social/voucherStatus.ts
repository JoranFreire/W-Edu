import type { VoucherStatus } from '@/types/benefitVouchers';

export const voucherStatusLabels: Record<VoucherStatus, string> = {
  released: 'Liberado',
  redeemed: 'Retirado',
  cancelled: 'Cancelado',
  expired: 'Vencido',
};

export const voucherStatusClasses: Record<VoucherStatus, string> = {
  released: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  redeemed: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300',
  cancelled: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  expired: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
};

/** Disponivel para novas entregas: estoque fisico menos o que esta liberado em QR. */
export function availableStock(item: { stock: number; reserved: number }) {
  return item.stock - item.reserved;
}
