'use client';

import toast from 'react-hot-toast';
import SaasPlanForm from '@/components/saas/SaasPlanForm';
import StatusBadge from '@/components/common/StatusBadge';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSaasPlans } from '@/lib/hooks/platform/useSaasPlans';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { SaasPlan } from '@/types/saas';

/** Catalogo de planos SaaS que a plataforma cobra das instituicoes. */
export default function SaasPlansPage() {
  const { plans, error, create, setActive } = useSaasPlans();
  useErrorToast(error, 'Erro ao carregar os planos.');
  const toggle = async (plan: SaasPlan) => {
    try {
      await setActive(plan.id, !plan.is_active);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao atualizar o plano.'));
    }
  };
  return (
    <div className="max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Planos SaaS</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Preço mensal e limite de alunos ativos de cada plano.</p>
      </div>
      <section className={`${sectionCls} space-y-4`}>
        <SaasPlanForm onSubmit={create} />
        {plans.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum plano.</p> : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {plans.map((plan) => (
              <li key={plan.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <p className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200">
                  <strong className="text-gray-900 dark:text-white">{plan.name}</strong> · {formatMoney(plan.monthly_price_cents)}/mês ·{' '}
                  {plan.max_students !== null ? `até ${plan.max_students} alunos` : 'sem limite de alunos'}
                  <StatusBadge active={plan.is_active} activeLabel="Ativo" inactiveLabel="Inativo" />
                </p>
                <button onClick={() => toggle(plan)} aria-label={`${plan.is_active ? 'Desativar' : 'Ativar'} ${plan.name}`} className={secondaryButtonCls}>
                  {plan.is_active ? 'Desativar' : 'Ativar'}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
