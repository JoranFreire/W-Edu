'use client';

import { useState } from 'react';
import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, iconButtonCls, sectionCls } from '@/components/common/formStyles';
import { assessmentKindLabels, formatScore } from '@/lib/academic/assessmentLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { type AssessmentItemInput, useAssessmentItems } from '@/lib/hooks/teaching/useAssessmentItems';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { GradingPeriod } from '@/types/academicCalendar';
import type { AssessmentItem } from '@/types/assessment';
import AssessmentItemForm from './AssessmentItemForm';
import GradeEntryModal from './GradeEntryModal';

/** Avaliacoes da turma por etapa, com lancamento de notas. */
export default function AssessmentPlanPanel({ offeringId, periods, onGradesChanged }: {
  offeringId: number;
  periods: GradingPeriod[];
  onGradesChanged: () => void;
}) {
  const { items, error, create, remove } = useAssessmentItems(offeringId);
  const [grading, setGrading] = useState<AssessmentItem | null>(null);
  useErrorToast(error, 'Erro ao carregar avaliações.');
  const period = (id: number | null) => periods.find((candidate) => candidate.id === id);
  const locked = (item: AssessmentItem) => period(item.grading_period_id)?.status === 'closed';

  const handleCreate = async (input: AssessmentItemInput) => {
    await create(input);
    onGradesChanged();
  };

  const handleRemove = async (item: AssessmentItem) => {
    if (!window.confirm(`Excluir "${item.name}" e suas notas?`)) return;
    try {
      await remove(item.id);
      onGradesChanged();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir avaliação.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Plano de avaliações</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma avaliação planejada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {items.map((item) => (
            <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{item.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {assessmentKindLabels[item.kind]} · {period(item.grading_period_id)?.name ?? 'Sem etapa'} · peso {formatScore(item.weight)} · máx. {formatScore(item.max_score)}
                  {locked(item) && ' · etapa encerrada'}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => setGrading(item)} aria-label={`Lançar notas de ${item.name}`} className={iconButtonCls}><PencilSquareIcon className="h-4 w-4" /></button>
                {!locked(item) && (
                  <button onClick={() => handleRemove(item)} aria-label={`Excluir ${item.name}`} className={dangerIconButtonCls}><TrashIcon className="h-4 w-4" /></button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      <AssessmentItemForm periods={periods} onCreate={handleCreate} />
      {grading && <GradeEntryModal item={grading} onSaved={onGradesChanged} onClose={() => setGrading(null)} />}
    </section>
  );
}
