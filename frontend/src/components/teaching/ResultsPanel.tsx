'use client';

import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useOfferingResults } from '@/lib/hooks/teaching/useOfferingResults';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { GradingPeriod } from '@/types/academicCalendar';
import FinalResultsTable from './FinalResultsTable';
import PeriodClosureBar from './PeriodClosureBar';
import RecoveryForm from './RecoveryForm';

/** Fechamento de etapas, calculo do resultado, recuperacao e publicacao (coordenacao). */
export default function ResultsPanel({ offeringId, periods, isCoordination, onChanged }: {
  offeringId: string;
  periods: GradingPeriod[];
  isCoordination: boolean;
  onChanged: () => void;
}) {
  const { results, error, closePeriod, reopenPeriod, compute, saveRecovery, finalize } = useOfferingResults(offeringId);
  useErrorToast(error, 'Erro ao carregar resultados.');

  const attempt = async (action: () => Promise<void>, success: string, confirm?: string) => {
    if (confirm && !window.confirm(confirm)) return;
    try {
      await action();
      toast.success(success);
      onChanged();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir a ação.'));
    }
  };

  if (!results) return <Spinner variant="panel" />;
  const inRecovery = results.rows.filter((row) => row.result === 'recovery' || (row.result === 'failed' && row.recovery_score !== null));
  return (
    <section className={`${sectionCls} space-y-5`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Resultado da turma</h2>
        {results.finalized ? (
          <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300">Resultado publicado</span>
        ) : (
          <div className="flex flex-wrap gap-2">
            <button onClick={() => attempt(compute, 'Resultado calculado.')} className={secondaryButtonCls}>Calcular resultado</button>
            {isCoordination && (
              <button onClick={() => attempt(finalize, 'Resultado publicado.', 'Publicar o resultado? A turma será finalizada e os lançamentos bloqueados.')} className={primaryButtonCls}>
                Publicar resultado
              </button>
            )}
          </div>
        )}
      </div>
      <PeriodClosureBar
        periods={periods}
        closedIds={results.closed_period_ids}
        finalized={results.finalized}
        canReopen={isCoordination}
        onClose={(period) => attempt(() => closePeriod(period.id), `${period.name} fechada.`, `Fechar ${period.name}? Notas e diário do período ficam bloqueados.`)}
        onReopen={(period) => attempt(() => reopenPeriod(period.id), `${period.name} reaberta.`)}
      />
      <FinalResultsTable results={results} periods={periods} />
      {!results.finalized && results.scheme.recovery_enabled && inRecovery.length > 0 && (
        <RecoveryForm
          key={inRecovery.map((row) => `${row.class_enrollment_id}:${row.recovery_score}`).join('|')}
          rows={inRecovery}
          maxScore={results.scheme.max_value}
          onSave={saveRecovery}
        />
      )}
    </section>
  );
}
