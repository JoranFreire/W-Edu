import StatusBadge from '@/components/common/StatusBadge';
import { primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { formatIsoDate } from '@/lib/dates';
import { tuitionBasisLabels } from '@/lib/finance/tuitionLabels';
import type { TuitionPlan } from '@/types/tuition';

export default function TuitionPlansList({ plans, onGenerate, onToggle }: {
  plans: TuitionPlan[];
  onGenerate: (plan: TuitionPlan) => void;
  onToggle: (plan: TuitionPlan) => void;
}) {
  if (plans.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum plano de mensalidade.</p>;
  return (
    <ul className="divide-y divide-gray-100 dark:divide-gray-700">
      {plans.map((plan) => (
        <li key={plan.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
          <div className="space-y-1">
            <p className="flex items-center gap-2 font-medium text-gray-900 dark:text-white">{plan.name} <StatusBadge active={plan.is_active} activeLabel="Ativo" inactiveLabel="Inativo" /></p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {[tuitionBasisLabels[plan.basis], plan.term_name, plan.class_group_name ?? plan.program_name ?? 'Todos os programas',
                `${plan.installments}x de ${formatMoney(plan.amount_cents)}${plan.basis === 'credit' ? ' por crédito' : ''}`,
                `a partir de ${formatIsoDate(plan.first_due_on)}`].join(' · ')}
            </p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => onToggle(plan)} aria-label={`${plan.is_active ? 'Desativar' : 'Ativar'} ${plan.name}`} className={secondaryButtonCls}>
              {plan.is_active ? 'Desativar' : 'Ativar'}
            </button>
            {plan.is_active && (
              <button onClick={() => onGenerate(plan)} aria-label={`Gerar cobranças de ${plan.name}`} className={primaryButtonCls}>Gerar cobranças</button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
