import { formatScore } from '@/lib/academic/assessmentLabels';
import { componentKindLabels } from '@/lib/academic/labels';
import { transcriptStatusLabels } from '@/lib/academic/secretariatLabels';
import type { Transcript, TranscriptStatus } from '@/types/secretariat';

const statusStyles: Record<TranscriptStatus, string> = {
  completed: 'text-emerald-700 dark:text-emerald-300',
  credited: 'text-indigo-700 dark:text-indigo-300',
  in_progress: 'text-amber-700 dark:text-amber-300',
  failed: 'text-red-600 dark:text-red-400',
  pending: 'text-gray-500 dark:text-gray-400',
};

/** Historico escolar: disciplinas da matriz por periodo, situacao, nota, CR e integralizacao. */
export default function TranscriptTable({ transcript, termLabel }: { transcript: Transcript; termLabel: string }) {
  const { summary } = transcript;
  const stats = [
    { label: 'CR', value: formatScore(summary.cr) },
    { label: 'Integralização', value: `${formatScore(summary.integralization)}%` },
    { label: 'Carga cumprida', value: `${summary.hours_done}h` },
    { label: 'Componentes', value: `${summary.completed_components}/${summary.total_components}` },
  ];
  return (
    <div className="space-y-4">
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
            <dt className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</dt>
            <dd className="text-lg font-semibold text-gray-900 dark:text-white">{stat.value}</dd>
          </div>
        ))}
      </dl>
      <div className="h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700" role="progressbar" aria-label="Integralização"
        aria-valuenow={summary.integralization} aria-valuemin={0} aria-valuemax={100}>
        <div className="h-full bg-indigo-600" style={{ width: `${Math.min(summary.integralization, 100)}%` }} />
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-left text-xs uppercase text-gray-500 dark:text-gray-400">
            <tr>
              <th className="py-2 pr-4">{termLabel}</th><th className="py-2 pr-4">Disciplina</th><th className="py-2 pr-4">Tipo</th>
              <th className="py-2 pr-4">CH</th><th className="py-2 pr-4">Nota</th><th className="py-2 pr-4">Cursada em</th><th className="py-2">Situação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {transcript.rows.map((row) => (
              <tr key={row.subject_id} className="text-gray-800 dark:text-gray-200">
                <td className="py-2 pr-4">{row.term_number}</td>
                <td className="py-2 pr-4">{row.code} · {row.name}</td>
                <td className="py-2 pr-4">{componentKindLabels[row.kind]}</td>
                <td className="py-2 pr-4">{row.hours}h</td>
                <td className="py-2 pr-4">{formatScore(row.grade)}</td>
                <td className="py-2 pr-4">{row.taken_in ?? '—'}</td>
                <td className={`py-2 font-medium ${statusStyles[row.status]}`}>{transcriptStatusLabels[row.status]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
