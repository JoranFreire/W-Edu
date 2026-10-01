'use client';

import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { formatIsoDate } from '@/lib/dates';
import { useMyBenefits } from '@/lib/hooks/social/useMyBenefits';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Beneficios recebidos pelo aluno (lanche, material, transporte...). */
export default function MyBenefitsPage() {
  const { deliveries, loading, error } = useMyBenefits();
  useErrorToast(error, 'Erro ao carregar os benefícios.');
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Benefícios recebidos</h1>
      <section className={sectionCls}>
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
