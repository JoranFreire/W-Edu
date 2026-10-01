'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { agendaKindLabels } from '@/lib/academic/schoolLifeLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { AgendaItemInput, AgendaItemKind } from '@/types/schoolLife';

/** Publica item na agenda da turma, opcionalmente ligado a oferta (disciplina). */
export default function AgendaItemForm({ offeringId, onSubmit }: {
  offeringId: number | null;
  onSubmit: (input: AgendaItemInput) => Promise<void>;
}) {
  const empty: AgendaItemInput = { kind: 'homework', title: '', description: null, due_on: todayIso(), class_offering_id: offeringId };
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<AgendaItemInput>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({ ...draft, description: draft.description || null });
      setDraft(empty);
      toast.success('Publicado na agenda.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao publicar na agenda.'));
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <select aria-label="Tipo do item" value={draft.kind} onChange={(e) => set({ kind: e.target.value as AgendaItemKind })} className={inputCls}>
          {optionsOf(agendaKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <input required aria-label="Título do item" value={draft.title} onChange={(e) => set({ title: e.target.value })} placeholder="Título" className={`${inputCls} md:col-span-2`} />
        <input required type="date" aria-label="Data do item" value={draft.due_on} onChange={(e) => set({ due_on: e.target.value })} className={inputCls} />
      </div>
      <textarea aria-label="Detalhes do item" value={draft.description ?? ''} onChange={(e) => set({ description: e.target.value })}
        placeholder="Detalhes (opcional)" rows={2} className={inputCls} />
      <div className="flex justify-end">
        <button className={primaryButtonCls}>Publicar</button>
      </div>
    </form>
  );
}
