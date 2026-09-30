import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import type { CurriculumDetail } from '@/types/academic';

/** Totais da matriz e pendencias de coerencia (pre-requisitos, duracao). */
export default function CurriculumSummary({ detail, termLabel }: { detail: CurriculumDetail; termLabel: string }) {
  const stats = [
    { label: 'Carga horária', value: `${detail.totals.hours}h` },
    { label: 'Obrigatórias', value: `${detail.totals.mandatory_hours}h` },
    { label: 'Créditos', value: detail.totals.credits },
    { label: `${termLabel}s`, value: detail.totals.terms },
  ];
  return (
    <div className="space-y-3">
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
            <dt className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</dt>
            <dd className="text-lg font-semibold text-gray-900 dark:text-white">{stat.value}</dd>
          </div>
        ))}
      </dl>
      {detail.issues.length > 0 && (
        <div role="status" className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-200">
          <p className="mb-1 flex items-center gap-2 font-medium"><ExclamationTriangleIcon className="h-4 w-4" /> Pendências</p>
          <ul className="list-disc space-y-0.5 pl-6">
            {detail.issues.map((issue) => <li key={issue}>{issue}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
