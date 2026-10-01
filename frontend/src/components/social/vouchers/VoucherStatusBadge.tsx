import { voucherStatusClasses, voucherStatusLabels } from '@/lib/social/voucherStatus';
import type { VoucherStatus } from '@/types/benefitVouchers';

export default function VoucherStatusBadge({ status }: { status: VoucherStatus }) {
  return <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${voucherStatusClasses[status]}`}>{voucherStatusLabels[status]}</span>;
}
