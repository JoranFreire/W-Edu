'use client';

import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useEnrollmentFinance } from '@/lib/hooks/tuition/useEnrollmentFinance';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Discount } from '@/types/tuition';
import DiscountForm from './DiscountForm';
import DiscountsList from './DiscountsList';
import SettleButton from './SettleButton';
import TuitionStatement from './TuitionStatement';

/** Aba Financeiro da ficha: bolsas e descontos, extrato e (administracao) baixa das parcelas. */
export default function EnrollmentFinanceTab({ enrollmentId, canSettle }: { enrollmentId: string; canSettle: boolean }) {
  const { finance, error, addDiscount, deactivateDiscount, settle } = useEnrollmentFinance(enrollmentId);
  useErrorToast(error, 'Erro ao carregar o financeiro da matrícula.');

  const handleDeactivate = async (discount: Discount) => {
    try {
      await deactivateDiscount(discount.id);
      toast.success('Desconto encerrado.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao encerrar o desconto.'));
    }
  };

  if (!finance) return <Spinner />;
  return (
    <div className="space-y-6">
      <section className={`${sectionCls} space-y-4`}>
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Bolsas e descontos</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Valem nas parcelas geradas dentro da vigência; pontualidade só até o vencimento.</p>
        </div>
        <DiscountForm onSubmit={addDiscount} />
        <DiscountsList discounts={finance.discounts} onDeactivate={handleDeactivate} />
      </section>
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Mensalidades</h2>
        <TuitionStatement
          charges={finance.charges}
          actions={canSettle ? (charge) => (charge.quote ? <SettleButton charge={charge} onSettle={(input) => settle(charge.id, input)} /> : null) : undefined}
        />
      </section>
    </div>
  );
}
