'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { assessmentKindLabels } from '@/lib/academic/assessmentLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import type { AssessmentItemInput } from '@/lib/hooks/teaching/useAssessmentItems';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { GradingPeriod } from '@/types/academicCalendar';
import type { AssessmentKind } from '@/types/assessment';

const emptyDraft = { name: '', kind: 'test' as AssessmentKind, grading_period_id: '', weight: '1', max_score: '10', quiz_id: '' };

/** Inclusao de avaliacao no plano da turma. */
export default function AssessmentItemForm({ periods, onCreate }: {
  periods: GradingPeriod[];
  onCreate: (input: AssessmentItemInput) => Promise<void>;
}) {
  const labels = useTerminology();
  const [draft, setDraft] = useState(emptyDraft);
  const set = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });
  const openPeriods = periods.filter((period) => period.status === 'open');

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onCreate({
        name: draft.name,
        kind: draft.kind,
        grading_period_id: draft.grading_period_id ? draft.grading_period_id : null,
        weight: Number(draft.weight),
        max_score: Number(draft.max_score),
        quiz_id: draft.kind === 'quiz' && draft.quiz_id ? draft.quiz_id : null,
        due_on: null,
      });
      setDraft(emptyDraft);
      toast.success('Avaliação incluída.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao incluir avaliação.'));
    }
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-2 gap-3 md:grid-cols-[1.6fr_1fr_1fr_0.6fr_0.7fr_auto]">
      <input required aria-label="Nome da avaliação" value={draft.name} onChange={(e) => set({ name: e.target.value })} placeholder="Ex.: Prova 1" className={`${inputCls} col-span-2 md:col-span-1`} />
      <select aria-label="Tipo" value={draft.kind} onChange={(e) => set({ kind: e.target.value as AssessmentKind })} className={inputCls}>
        {optionsOf(assessmentKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      <select aria-label={labels.gradingPeriod} value={draft.grading_period_id} onChange={(e) => set({ grading_period_id: e.target.value })} className={inputCls}>
        <option value="">Sem etapa</option>
        {openPeriods.map((period) => <option key={period.id} value={period.id}>{period.name}</option>)}
      </select>
      <input type="number" min={0} step="0.5" aria-label="Peso" value={draft.weight} onChange={(e) => set({ weight: e.target.value })} className={inputCls} />
      <input type="number" min={0.5} step="0.5" aria-label="Nota máxima" value={draft.max_score} onChange={(e) => set({ max_score: e.target.value })} className={inputCls} />
      <button className={primaryButtonCls}>Incluir</button>
      {draft.kind === 'quiz' && (
        <input type="number" min={1} aria-label="ID do quiz" value={draft.quiz_id} onChange={(e) => set({ quiz_id: e.target.value })} placeholder="Nº do quiz (opcional, para importar notas)" className={`${inputCls} col-span-2 md:col-span-3`} />
      )}
    </form>
  );
}
