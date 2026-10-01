'use client';

import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import VoucherList from '@/components/social/vouchers/VoucherList';
import { formatIsoDate } from '@/lib/dates';
import { useMyBenefits } from '@/lib/hooks/social/useMyBenefits';
import { useMyVouchers } from '@/lib/hooks/social/useMyVouchers';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Beneficios do aluno: os liberados (com o QR para a retirada) e os ja recebidos. */
export default function MyBenefitsPage() {
  const { deliveries, loading, error } = useMyBenefits();
  const vouchers = useMyVouchers();
  useErrorToast(error ?? vouchers.error, 'Erro ao carregar os benefícios.');
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Benefícios</h1>
      <section className={`${sectionCls} space-y-3`}>
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Liberados para retirada</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Mostre o QR na retirada (também está no app).</p>
        </div>
        {vouchers.loading && vouchers.vouchers.length === 0 ? <Spinner /> : <VoucherList vouchers={vouchers.vouchers} />}
      </section>
      <section className={`${sectionCls} space-y-3`}>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Recebidos</h2>
        {loading && deliveries.length === 0 ? <Spinner /> : deliveries.length === 0
          ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum benefício registrado.</p>
          : (
            <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
              {deliveries.map((delivery) => (
                <li key={delivery.id} className="py-2 text-gray-800 dark:text-gray-200">{formatIsoDate(delivery.delivered_on)} · {delivery.item_name} × {delivery.quantity}</li>
              ))}
            </ul>
          )}
      </section>
    </div>
  );
}
