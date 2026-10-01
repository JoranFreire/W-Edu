'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import InvoicesList from '@/components/saas/InvoicesList';
import SubscriptionForm from '@/components/saas/SubscriptionForm';
import UsageSummary from '@/components/saas/UsageSummary';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { inputCls, primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useInstitutionPlan } from '@/lib/hooks/platform/useInstitutionPlan';
import { useSaasPlans } from '@/lib/hooks/platform/useSaasPlans';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Plano SaaS de uma instituicao: assinatura, uso e faturas mensais. */
export default function InstitutionPlanPage() {
  const router = useRouter();
  const institutionId = useParams<{ institutionId: string }>().institutionId;
  const { overview, error, subscribe, generateInvoice, markPaid } = useInstitutionPlan(institutionId);
  const { plans } = useSaasPlans();
  const [periodStart, setPeriodStart] = useState('');
  useErrorToast(error, 'Erro ao carregar o plano da instituição.');

  const run = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir.'));
    }
  };

  if (!overview) return <Spinner />;
  const subscription = overview.subscription;
  return (
    <div className="max-w-5xl space-y-6">
      <BackButton label="Instituições" onClick={() => router.push('/platform/institutions')} />
      <section className={`${sectionCls} space-y-4`}>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Plano contratado</h1>
        <UsageSummary overview={overview} />
        <SubscriptionForm key={`${subscription?.plan.id}-${subscription?.status}`} subscription={subscription} plans={plans} onSubmit={subscribe} />
      </section>
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Faturas</h2>
        {subscription && (
          <form onSubmit={(event) => { event.preventDefault(); run(() => generateInvoice(periodStart), 'Fatura gerada.'); }} className="flex flex-wrap gap-3">
            <input required type="date" aria-label="Início do período da fatura" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} className={`${inputCls} w-48`} />
            <button className={primaryButtonCls}>Gerar fatura do período</button>
          </form>
        )}
        <InvoicesList
          invoices={overview.invoices}
          actions={(invoice) => invoice.status === 'pending'
            ? <button onClick={() => run(() => markPaid(invoice.id), 'Fatura quitada.')} className={secondaryButtonCls}>Marcar como paga</button>
            : null}
        />
      </section>
    </div>
  );
}
