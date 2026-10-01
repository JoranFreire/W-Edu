import { formatIsoDate } from '@/lib/dates';
import type { BenefitVoucher } from '@/types/benefitVouchers';
import VoucherQrCard from './VoucherQrCard';
import VoucherStatusBadge from './VoucherStatusBadge';

/** Liberados (com QR) em destaque; retirados, vencidos e cancelados no historico. */
export default function VoucherList({ vouchers }: { vouchers: BenefitVoucher[] }) {
  const released = vouchers.filter((voucher) => voucher.status === 'released');
  const history = vouchers.filter((voucher) => voucher.status !== 'released');
  return (
    <div className="space-y-4">
      {released.length === 0
        ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum benefício liberado para retirada.</p>
        : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {released.map((voucher) => <VoucherQrCard key={voucher.id} voucher={voucher} />)}
          </div>
        )}
      {history.length > 0 && (
        <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
          {history.map((voucher) => (
            <li key={voucher.id} className="flex items-center justify-between gap-3 py-2 text-gray-800 dark:text-gray-200">
              <span>{voucher.item_name} × {voucher.quantity} · {formatIsoDate((voucher.redeemed_at ?? voucher.released_at).slice(0, 10))}</span>
              <VoucherStatusBadge status={voucher.status} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
