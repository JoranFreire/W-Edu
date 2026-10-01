'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { InternshipLogInput } from '@/types/completion';

/** O aluno lanca horas do dia no diario de estagio. */
export default function InternshipLogForm({ onSubmit }: { onSubmit: (input: InternshipLogInput) => Promise<void> }) {
  const empty: InternshipLogInput = { worked_on: todayIso(), hours: 4, activities: '' };
  const [draft, setDraft] = useState(empty);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit(draft);
      setDraft(empty);
      toast.success('Horas registradas.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar as horas.'));
    }
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-6">
      <input required type="date" aria-label="Dia do estágio" value={draft.worked_on} onChange={(e) => setDraft({ ...draft, worked_on: e.target.value })} className={inputCls} />
      <input required type="number" min={1} max={12} aria-label="Horas no dia" value={draft.hours} onChange={(e) => setDraft({ ...draft, hours: Number(e.target.value) })} className={inputCls} />
      <input required aria-label="Atividades do dia" value={draft.activities} onChange={(e) => setDraft({ ...draft, activities: e.target.value })} placeholder="Atividades realizadas" className={`${inputCls} md:col-span-3`} />
      <button className={primaryButtonCls}>Registrar</button>
    </form>
  );
}
