'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import { discountKindLabels, reaisToCents } from '@/lib/finance/tuitionLabels';
import type { DiscountInput, DiscountKind } from '@/types/tuition';

/** Concede bolsa ou desconto: percentual ou valor fixo por parcela, com vigencia. */
export default function DiscountForm({ onSubmit }: { onSubmit: (input: DiscountInput) => Promise<void> }) {
  const empty = { kind: 'scholarship' as DiscountKind, mode: 'percent', value: '', validFrom: todayIso(), validUntil: '' };
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({
        kind: draft.kind, description: null, valid_from: draft.validFrom, valid_until: draft.validUntil || null,
        percent: draft.mode === 'percent' ? Number(draft.value.replace(',', '.')) : null,
        amount_cents: draft.mode === 'amount' ? reaisToCents(draft.value) : null,
      });
      setDraft(empty);
      toast.success('Desconto concedido.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao conceder o desconto.'));
    }
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-6">
      <select aria-label="Tipo de desconto" value={draft.kind} onChange={(e) => set({ kind: e.target.value as DiscountKind })} className={inputCls}>
        {optionsOf(discountKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      <select aria-label="Forma do desconto" value={draft.mode} onChange={(e) => set({ mode: e.target.value })} className={inputCls}>
        <option value="percent">Percentual (%)</option>
        <option value="amount">Valor fixo (R$)</option>
      </select>
      <input required inputMode="decimal" aria-label="Valor do desconto" value={draft.value} onChange={(e) => set({ value: e.target.value })} placeholder={draft.mode === 'percent' ? '50' : '0,00'} className={inputCls} />
      <input required type="date" aria-label="Início da vigência" value={draft.validFrom} onChange={(e) => set({ validFrom: e.target.value })} className={inputCls} />
      <input type="date" aria-label="Fim da vigência" value={draft.validUntil} onChange={(e) => set({ validUntil: e.target.value })} className={inputCls} />
      <button className={primaryButtonCls}>Conceder</button>
    </form>
  );
}
