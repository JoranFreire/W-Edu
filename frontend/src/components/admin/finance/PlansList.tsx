import { formatCents, periodLabels } from '@/lib/finance/labels';
import type { BillingPlan } from '@/types/finance';

export default function PlansList({ plans }: { plans: BillingPlan[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {plans.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhum plano cadastrado.</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {plans.map((plan) => (
            <div key={plan.id} className="px-5 py-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{plan.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{periodLabels[plan.billing_period]} • {formatCents(plan.price_cents)}</p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${plan.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
                {plan.is_active ? 'Ativo' : 'Inativo'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
