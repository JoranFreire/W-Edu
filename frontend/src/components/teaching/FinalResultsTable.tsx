import { formatScore } from '@/lib/academic/assessmentLabels';
import type { OfferingResults } from '@/types/assessment';
import type { GradingPeriod } from '@/types/academicCalendar';
import ResultBadge from './ResultBadge';

/** Medias consolidadas por etapa, recuperacao, nota final, frequencia e situacao. */
export default function FinalResultsTable({ results, periods }: { results: OfferingResults; periods: GradingPeriod[] }) {
  const shown = periods.filter((period) => results.closed_period_ids.includes(period.id));
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase text-gray-500 dark:text-gray-400">
          <tr>
            <th className="py-2 pr-4">Aluno</th>
            {shown.map((period) => <th key={period.id} className="py-2 pr-4">{period.name}</th>)}
            <th className="py-2 pr-4">Média</th>
            <th className="py-2 pr-4">Recuperação</th>
            <th className="py-2 pr-4">Final</th>
            <th className="py-2 pr-4">Frequência</th>
            <th className="py-2">Situação</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {results.rows.map((row) => (
            <tr key={row.class_enrollment_id} className="text-gray-800 dark:text-gray-200">
              <td className="py-2 pr-4">{row.student.name}</td>
              {shown.map((period) => (
                <td key={period.id} className="py-2 pr-4">{formatScore(row.periods.find((p) => p.grading_period_id === period.id)?.average)}</td>
              ))}
              <td className="py-2 pr-4">{formatScore(row.average)}</td>
              <td className="py-2 pr-4">{formatScore(row.recovery_score)}</td>
              <td className="py-2 pr-4 font-semibold">{formatScore(row.final_grade)}</td>
              <td className="py-2 pr-4">{row.attendance_rate === null ? '—' : `${formatScore(row.attendance_rate)}%`}</td>
              <td className="py-2"><ResultBadge result={row.result} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
