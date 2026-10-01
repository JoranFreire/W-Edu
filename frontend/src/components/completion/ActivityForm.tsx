'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { activityCategoryLabels } from '@/lib/academic/completionLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { ActivityCategory, ActivityInput } from '@/types/completion';

/** O aluno declara uma atividade complementar para analise da secretaria. */
export default function ActivityForm({ onSubmit }: { onSubmit: (input: ActivityInput) => Promise<void> }) {
  const empty: ActivityInput = { category: 'extension', title: '', description: null, occurred_on: todayIso(), hours_requested: 1 };
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<ActivityInput>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({ ...draft, description: draft.description || null });
      setDraft(empty);
      toast.success('Atividade enviada para análise.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao enviar a atividade.'));
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <input required aria-label="Título da atividade" value={draft.title} onChange={(e) => set({ title: e.target.value })} placeholder="Atividade" className={`${inputCls} md:col-span-2`} />
        <select aria-label="Categoria da atividade" value={draft.category} onChange={(e) => set({ category: e.target.value as ActivityCategory })} className={inputCls}>
          {optionsOf(activityCategoryLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <div className="grid grid-cols-2 gap-3">
          <input required type="date" aria-label="Data da atividade" value={draft.occurred_on} onChange={(e) => set({ occurred_on: e.target.value })} className={inputCls} />
          <input required type="number" min={1} aria-label="Horas da atividade" value={draft.hours_requested} onChange={(e) => set({ hours_requested: Number(e.target.value) })} className={inputCls} />
        </div>
      </div>
      <textarea aria-label="Descrição da atividade" value={draft.description ?? ''} onChange={(e) => set({ description: e.target.value })}
        placeholder="Detalhes e comprovação (opcional)" rows={2} className={inputCls} />
      <div className="flex justify-end"><button className={primaryButtonCls}>Enviar atividade</button></div>
    </form>
  );
}
