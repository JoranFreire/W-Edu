import { formatMoney } from '@/lib/academic/guardianLabels';
import { formatIsoDate } from '@/lib/dates';
import { subscriptionStatusLabels } from '@/lib/platform/saasLabels';
import type { InstitutionPlan } from '@/types/saas';

/** Plano contratado, situacao e uso de alunos ativos frente ao limite. */
export default function UsageSummary({ overview }: { overview: InstitutionPlan }) {
  const { subscription, usage } = overview;
  if (!subscription) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum plano contratado.</p>;
  return (
    <div className="space-y-1 text-sm text-gray-700 dark:text-gray-200">
      <p>
        <strong className="text-gray-900 dark:text-white">{subscription.plan.name}</strong> · {formatMoney(subscription.plan.monthly_price_cents)}/mês ·{' '}
        {subscriptionStatusLabels[subscription.status]}{subscription.trial_ends_on ? ` até ${formatIsoDate(subscription.trial_ends_on)}` : ''}
      </p>
      <p>Alunos ativos: {usage.active_students}{usage.max_students !== null ? ` de ${usage.max_students}` : ' (sem limite)'}</p>
    </div>
  );
}
