import StatusBadge from '@/components/common/StatusBadge';
import { secondaryButtonCls } from '@/components/common/formStyles';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { formatIsoDate } from '@/lib/dates';
import { discountKindLabels } from '@/lib/finance/tuitionLabels';
import type { Discount } from '@/types/tuition';

export default function DiscountsList({ discounts, onDeactivate }: { discounts: Discount[]; onDeactivate: (discount: Discount) => void }) {
  if (discounts.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma bolsa ou desconto.</p>;
  return (
    <ul className="divide-y divide-gray-100 dark:divide-gray-700">
      {discounts.map((discount) => {
        const value = discount.percent !== null ? `${discount.percent}%` : formatMoney(discount.amount_cents ?? 0);
        const label = `${discountKindLabels[discount.kind]} de ${value}`;
        return (
          <li key={discount.id} className="flex flex-wrap items-center justify-between gap-3 py-2 text-sm">
            <span className="flex items-center gap-2 text-gray-800 dark:text-gray-200">
              {label} · desde {formatIsoDate(discount.valid_from)}{discount.valid_until ? ` até ${formatIsoDate(discount.valid_until)}` : ''}
              <StatusBadge active={discount.is_active} activeLabel="Vigente" inactiveLabel="Encerrado" />
            </span>
            {discount.is_active && (
              <button onClick={() => onDeactivate(discount)} aria-label={`Encerrar ${label}`} className={secondaryButtonCls}>Encerrar</button>
            )}
          </li>
        );
      })}
    </ul>
  );
}
