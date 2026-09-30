import ResultBadge from '@/components/teaching/ResultBadge';
import { formatScore } from '@/lib/academic/assessmentLabels';
import type { ReportCardEntry } from '@/types/assessment';

/** Boletim: uma linha por turma, com as etapas fechadas e o resultado publicado. */
export default function ReportCardList({ entries }: { entries: ReportCardEntry[] }) {
  if (entries.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">Ainda não há notas publicadas.</p>;
  }
  return (
    <ul className="space-y-4">
      {entries.map((entry) => (
        <li key={entry.class_offering_id} className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h2 className="font-semibold text-gray-900 dark:text-white">{entry.offering_name}</h2>
            <ResultBadge result={entry.result} />
          </div>
          <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {entry.periods.map((period) => (
              <div key={period.name} className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
                <dt className="text-xs text-gray-500 dark:text-gray-400">{period.name}</dt>
                <dd className="text-lg font-semibold text-gray-900 dark:text-white">{formatScore(period.average)}</dd>
                <dd className="text-xs text-gray-500 dark:text-gray-400">{period.absences} falta(s)</dd>
              </div>
            ))}
            {entry.finalized && (
              <div className="rounded-lg bg-indigo-50 p-3 dark:bg-indigo-900/20">
                <dt className="text-xs text-indigo-700 dark:text-indigo-300">Nota final</dt>
                <dd className="text-lg font-semibold text-indigo-900 dark:text-white">{formatScore(entry.final_grade)}</dd>
                <dd className="text-xs text-indigo-700 dark:text-indigo-300">
                  Frequência {entry.attendance_rate === null ? '—' : `${formatScore(entry.attendance_rate)}%`}
                </dd>
              </div>
            )}
          </dl>
          <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
            Aprovação com média {formatScore(entry.passing_grade)} e {entry.min_attendance}% de frequência.
          </p>
        </li>
      ))}
    </ul>
  );
}
