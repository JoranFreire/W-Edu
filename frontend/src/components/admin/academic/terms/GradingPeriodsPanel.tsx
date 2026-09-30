'use client';

import { useState } from 'react';
import { LockClosedIcon, LockOpenIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import StatusBadge from '@/components/common/StatusBadge';
import { dangerIconButtonCls, iconButtonCls, inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { gradingPeriodStatusLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { type GradingPeriodInput, useGradingPeriods } from '@/lib/hooks/admin/academic/useGradingPeriods';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { GradingPeriod } from '@/types/academicCalendar';

const emptyDraft: GradingPeriodInput = { name: '', starts_on: '', ends_on: '', weight: 1 };

/** Etapas de avaliacao do periodo: inclusao, encerramento/reabertura e exclusao. */
export default function GradingPeriodsPanel({ termId, editable, canDelete }: { termId: number; editable: boolean; canDelete: boolean }) {
  const terms = useTerminology();
  const { periods, error, save, changeStatus, remove } = useGradingPeriods(termId);
  const [draft, setDraft] = useState(emptyDraft);
  useErrorToast(error, 'Erro ao carregar etapas.');

  const attempt = async (action: () => Promise<void>, success?: string) => {
    try {
      await action();
      if (success) toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir a ação.'));
    }
  };

  const handleAdd = (event: React.FormEvent) => {
    event.preventDefault();
    attempt(async () => {
      await save(null, draft);
      setDraft(emptyDraft);
    }, 'Etapa criada.');
  };

  const toggle = (period: GradingPeriod) =>
    attempt(() => changeStatus(period.id, period.status === 'open' ? 'closed' : 'open'));

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">{terms.gradingPeriods}</h2>
      {periods.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma etapa cadastrada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {periods.map((period) => (
            <li key={period.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{period.order}. {period.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {formatIsoDate(period.starts_on)} a {formatIsoDate(period.ends_on)} · peso {period.weight}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <StatusBadge active={period.status === 'open'} activeLabel={gradingPeriodStatusLabels.open} inactiveLabel={gradingPeriodStatusLabels.closed} />
                {editable && (
                  <button onClick={() => toggle(period)} aria-label={`${period.status === 'open' ? 'Encerrar' : 'Reabrir'} ${period.name}`} className={iconButtonCls}>
                    {period.status === 'open' ? <LockClosedIcon className="h-4 w-4" /> : <LockOpenIcon className="h-4 w-4" />}
                  </button>
                )}
                {canDelete && editable && period.status === 'open' && (
                  <button onClick={() => attempt(() => remove(period.id), 'Etapa excluída.')} aria-label={`Excluir ${period.name}`} className={dangerIconButtonCls}>
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editable && (
        <form onSubmit={handleAdd} className="grid grid-cols-1 gap-3 sm:grid-cols-[1.5fr_1fr_1fr_0.6fr_auto]">
          <input required aria-label="Nome da etapa" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} placeholder={`Ex.: 1º ${terms.gradingPeriod.toLowerCase()}`} className={inputCls} />
          <input required type="date" aria-label="Início da etapa" value={draft.starts_on} onChange={(e) => setDraft({ ...draft, starts_on: e.target.value })} className={inputCls} />
          <input required type="date" aria-label="Fim da etapa" value={draft.ends_on} onChange={(e) => setDraft({ ...draft, ends_on: e.target.value })} className={inputCls} />
          <input type="number" min={0} step="0.5" aria-label="Peso" value={draft.weight} onChange={(e) => setDraft({ ...draft, weight: Number(e.target.value) })} className={inputCls} />
          <button className={primaryButtonCls}>Adicionar etapa</button>
        </form>
      )}
    </section>
  );
}
