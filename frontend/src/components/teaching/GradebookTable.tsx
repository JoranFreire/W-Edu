import { formatScore } from '@/lib/academic/assessmentLabels';
import type { Gradebook } from '@/types/assessment';

/** Boletim parcial: media por etapa, media geral, conceito e frequencia de cada aluno. */
export default function GradebookTable({ gradebook }: { gradebook: Gradebook }) {
  const { scheme, periods, rows } = gradebook;
  if (rows.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno inscrito na turma.</p>;
  }
  const passing = (value: number | null) => value !== null && value >= scheme.passing_grade;
  const attendanceOk = (rate: number | null) => rate === null || rate >= scheme.min_attendance;
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase text-gray-500 dark:text-gray-400">
          <tr>
            <th className="py-2 pr-4">Aluno</th>
            {periods.map((period) => <th key={period.id ?? 'none'} className="py-2 pr-4">{period.name}</th>)}
            <th className="py-2 pr-4">Média</th>
            {scheme.scale === 'concept' && <th className="py-2 pr-4">Conceito</th>}
            <th className="py-2 pr-4">Faltas</th>
            <th className="py-2">Frequência</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {rows.map((row) => (
            <tr key={row.class_enrollment_id} className="text-gray-800 dark:text-gray-200">
              <td className="py-2 pr-4">{row.student.name}</td>
              {periods.map((period) => (
                <td key={period.id ?? 'none'} className="py-2 pr-4">{formatScore(row.period_averages[String(period.id ?? 'none')])}</td>
              ))}
              <td className={`py-2 pr-4 font-semibold ${row.average === null ? '' : passing(row.average) ? 'text-emerald-600' : 'text-red-600'}`}>
                {formatScore(row.average)}
              </td>
              {scheme.scale === 'concept' && <td className="py-2 pr-4">{row.concept ?? '—'}</td>}
              <td className="py-2 pr-4">{row.absences}</td>
              <td className={`py-2 ${attendanceOk(row.attendance_rate) ? '' : 'font-semibold text-red-600'}`}>
                {row.attendance_rate === null ? '—' : `${formatScore(row.attendance_rate)}%`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
        {scheme.name}: aprovação com média {formatScore(scheme.passing_grade)} e {scheme.min_attendance}% de frequência · {gradebook.total_lessons} aulas registradas. Prévia; o fechamento da etapa consolida os valores.
      </p>
    </div>
  );
}
