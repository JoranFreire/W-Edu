'use client';

import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { riskCls, riskLabels } from '@/lib/academic/socialLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useRetentionReport } from '@/lib/hooks/retention/useRetentionReport';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Frequencia por aluno com nivel de risco; a secretaria/coordenacao readmite quem foi desligado. */
export default function RetentionPanel({ offeringId, canReadmit }: { offeringId: string; canReadmit: boolean }) {
  const { report, error, readmit } = useRetentionReport(offeringId);
  useErrorToast(error, 'Erro ao carregar a frequência.');
  if (!report) return <Spinner />;
  const handleReadmit = async (enrollmentId: string) => {
    try {
      await readmit(enrollmentId);
      toast.success('Aluno readmitido.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível readmitir.'));
    }
  };
  return (
    <section className={`${sectionCls} space-y-3`}>
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Frequência e risco de evasão</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {report.max_absence_percent !== null
            ? `Limite de faltas: ${report.max_absence_percent}% do curso; acima dele o aluno é desligado ao encerrar o encontro.`
            : 'Turma sem limite de faltas: o risco é calculado com 25%, sem desligamento.'}
        </p>
      </div>
      {report.rows.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno.</p> : (
        <ul className="divide-y divide-gray-100 dark:divide-gray-700">
          {report.rows.map((row) => (
            <li key={row.class_enrollment_id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
              <span className="text-gray-800 dark:text-gray-200">
                <strong className="text-gray-900 dark:text-white">{row.student.name}</strong> · {row.absences} falta(s) em {row.sessions} · {row.absence_percent.toLocaleString('pt-BR')}%
                {row.trailing_absences >= 2 ? ` · ${row.trailing_absences} seguidas` : ''}
                <span className={`ml-2 rounded-full px-2 py-0.5 text-xs font-medium ${riskCls[row.level]}`}>{riskLabels[row.level]}</span>
                {row.dismissed_at && <span className="ml-2 text-xs text-red-700 dark:text-red-300">Desligado: {row.dismissal_reason}</span>}
              </span>
              {row.dismissed_at && canReadmit && (
                <button onClick={() => handleReadmit(row.class_enrollment_id)} aria-label={`Readmitir ${row.student.name}`} className={secondaryButtonCls}>Readmitir</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
