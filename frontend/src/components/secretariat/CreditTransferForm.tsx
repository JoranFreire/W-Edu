'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { toOptionalInt } from '@/lib/forms/numbers';
import type { CreditTransferInput } from '@/lib/hooks/secretariat/useCreditTransfers';
import type { TranscriptRow } from '@/types/secretariat';

const empty = { subject_id: '', source_institution: '', source_subject: '', grade: '', hours: '' };

/** Pedido de aproveitamento para uma disciplina ainda nao cumprida da matriz. */
export default function CreditTransferForm({ pending, onRequest }: {
  pending: Pick<TranscriptRow, 'subject_id' | 'code' | 'name'>[];
  onRequest: (input: CreditTransferInput) => Promise<void>;
}) {
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onRequest({
        subject_id: Number(draft.subject_id),
        origin: draft.source_institution ? 'external' : 'internal',
        source_institution: draft.source_institution || null,
        source_subject: draft.source_subject,
        grade: draft.grade ? Number(draft.grade.replace(',', '.')) : null,
        hours: toOptionalInt(draft.hours),
      });
      setDraft(empty);
      toast.success('Aproveitamento registrado para análise.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar aproveitamento.'));
    }
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-2 gap-3 md:grid-cols-[1.5fr_1.2fr_1.2fr_0.6fr_0.6fr_auto]">
      <select required aria-label="Disciplina a aproveitar" value={draft.subject_id} onChange={(e) => set({ subject_id: e.target.value })} className={`${inputCls} col-span-2 md:col-span-1`}>
        <option value="">Disciplina da matriz...</option>
        {pending.map((row) => <option key={row.subject_id} value={row.subject_id}>{row.code} · {row.name}</option>)}
      </select>
      <input aria-label="Instituição de origem" value={draft.source_institution} onChange={(e) => set({ source_institution: e.target.value })} placeholder="Instituição (vazio = interna)" className={inputCls} />
      <input required aria-label="Disciplina cursada" value={draft.source_subject} onChange={(e) => set({ source_subject: e.target.value })} placeholder="Disciplina cursada" className={inputCls} />
      <input inputMode="decimal" aria-label="Nota de origem" value={draft.grade} onChange={(e) => set({ grade: e.target.value })} placeholder="Nota" className={inputCls} />
      <input inputMode="numeric" aria-label="Carga horária de origem" value={draft.hours} onChange={(e) => set({ hours: e.target.value })} placeholder="CH" className={inputCls} />
      <button className={primaryButtonCls}>Registrar</button>
    </form>
  );
}
