import { subscriptionStatusLabels } from '@/lib/finance/labels';
import type { Subscription } from '@/types/finance';

type NameLookup = (id: string | null) => string | null;

export default function SubscriptionsList({ subscriptions, planName, holderName }: {
  subscriptions: Subscription[];
  planName: NameLookup;
  holderName: (studentId: string | null, organizationId: string | null) => string | null;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {subscriptions.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhuma assinatura cadastrada.</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {subscriptions.map((subscription) => (
            <div key={subscription.id} className="px-5 py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{planName(subscription.billing_plan_id)}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {holderName(subscription.student_id, subscription.organization_id) || 'Sem titular'} • vence {new Date(subscription.current_period_end).toLocaleDateString('pt-BR')}
                </p>
              </div>
              <span className={`w-fit text-xs px-2 py-1 rounded-full font-medium ${subscription.status === 'active' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
                {subscriptionStatusLabels[subscription.status]}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
