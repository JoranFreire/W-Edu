import type { ReactNode } from 'react';
import { activityCategoryLabels, reviewStatusCls, reviewStatusLabels } from '@/lib/academic/completionLabels';
import { formatIsoDate } from '@/lib/dates';
import type { Activity } from '@/types/completion';

/** Atividades complementares; `actions` desenha os controles de cada uma (decisao ou retirada). */
export default function ActivityList({ activities, actions }: { activities: Activity[]; actions?: (activity: Activity) => ReactNode }) {
  if (activities.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma atividade declarada.</p>;
  return (
    <ul className="space-y-3">
      {activities.map((activity) => (
        <li key={activity.id} className="flex flex-wrap items-start justify-between gap-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <div className="space-y-1">
            <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
              {activity.title}
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${reviewStatusCls[activity.status]}`}>{reviewStatusLabels[activity.status]}</span>
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {activityCategoryLabels[activity.category]} · {formatIsoDate(activity.occurred_on)} · {activity.hours_requested}h solicitadas
              {activity.hours_approved !== null ? ` · ${activity.hours_approved}h aprovadas` : ''}
            </p>
            {activity.description && <p className="text-sm text-gray-600 dark:text-gray-300">{activity.description}</p>}
            {activity.decision_note && <p className="text-xs italic text-gray-500 dark:text-gray-400">{activity.decision_note}</p>}
          </div>
          {actions?.(activity)}
        </li>
      ))}
    </ul>
  );
}
