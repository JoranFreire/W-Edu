'use client';

import { sectionCls } from '@/components/common/formStyles';
import { useCurrentPlan } from '@/lib/hooks/admin/useCurrentPlan';
import InvoicesList from './InvoicesList';
import UsageSummary from './UsageSummary';

/** Plano contratado pela instituicao ativa (somente leitura para o admin da instituicao). */
export default function CurrentPlanSection() {
  const { overview } = useCurrentPlan();
  if (!overview) return null;
  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Plano contratado</h2>
      <UsageSummary overview={overview} />
      {overview.invoices.length > 0 && <InvoicesList invoices={overview.invoices} />}
    </section>
  );
}
