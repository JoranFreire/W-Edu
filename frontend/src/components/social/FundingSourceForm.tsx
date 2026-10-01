'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { fundingKindLabels } from '@/lib/academic/socialLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import { reaisToCents } from '@/lib/finance/tuitionLabels';
import type { FundingKind, FundingSourceInput } from '@/types/socialPrograms';

/** Novo financiador: tipo, instrumento (convenio/termo), valor e vigencia. */
export default function FundingSourceForm({ onSubmit }: { onSubmit: (input: FundingSourceInput) => Promise<void> }) {
  const empty = { name: '', kind: 'agreement' as FundingKind, agreement: '', amount: '', startsOn: todayIso(), endsOn: '' };
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({
        name: draft.name, kind: draft.kind, agreement_number: draft.agreement || null,
        amount_cents: draft.amount ? reaisToCents(draft.amount) : null, starts_on: draft.startsOn, ends_on: draft.endsOn || null, notes: null,
      });
      setDraft(empty);
      toast.success('Financiador cadastrado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao cadastrar o financiador.'));
    }
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-6">
      <input required aria-label="Nome do financiador" value={draft.name} onChange={(e) => set({ name: e.target.value })} placeholder="Nome" className={`${inputCls} md:col-span-2`} />
      <select aria-label="Tipo de financiador" value={draft.kind} onChange={(e) => set({ kind: e.target.value as FundingKind })} className={inputCls}>
        {optionsOf(fundingKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      <input aria-label="Número do convênio" value={draft.agreement} onChange={(e) => set({ agreement: e.target.value })} placeholder="Convênio/termo" className={inputCls} />
      <input inputMode="decimal" aria-label="Valor do financiamento" value={draft.amount} onChange={(e) => set({ amount: e.target.value })} placeholder="Valor (R$)" className={inputCls} />
      <input required type="date" aria-label="Início da vigência do financiador" value={draft.startsOn} onChange={(e) => set({ startsOn: e.target.value })} className={inputCls} />
      <div className="md:col-span-6 flex justify-end"><button className={primaryButtonCls}>Cadastrar financiador</button></div>
    </form>
  );
}
