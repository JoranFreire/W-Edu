'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { BenefitItem, FundingSource, StockEntryInput, StockOrigin } from '@/types/socialPrograms';

/** Entrada de estoque de um item: quantidade, compra ou doacao e financiador. */
export default function StockEntryForm({ item, fundingSources, onSubmit }: {
  item: BenefitItem;
  fundingSources: FundingSource[];
  onSubmit: (input: StockEntryInput) => Promise<void>;
}) {
  const [draft, setDraft] = useState({ quantity: '', origin: 'purchase' as StockOrigin, fundingId: '' });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({
        quantity: Number(draft.quantity), unit_cost_cents: null, origin: draft.origin,
        funding_source_id: draft.fundingId ? Number(draft.fundingId) : null, received_on: todayIso(),
      });
      setDraft({ ...draft, quantity: '' });
      toast.success('Estoque atualizado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao lançar o estoque.'));
    }
  };
  return (
    <form onSubmit={submit} className="flex flex-wrap items-center gap-2">
      <input required type="number" min={1} aria-label={`Quantidade de ${item.name}`} value={draft.quantity} onChange={(e) => setDraft({ ...draft, quantity: e.target.value })} placeholder="Qtd." className={`${inputCls} w-24`} />
      <select aria-label={`Origem de ${item.name}`} value={draft.origin} onChange={(e) => setDraft({ ...draft, origin: e.target.value as StockOrigin })} className={`${inputCls} w-32`}>
        <option value="purchase">Compra</option>
        <option value="donation">Doação</option>
      </select>
      <select aria-label={`Financiador de ${item.name}`} value={draft.fundingId} onChange={(e) => setDraft({ ...draft, fundingId: e.target.value })} className={`${inputCls} w-48`}>
        <option value="">Sem financiador</option>
        {fundingSources.map((funding) => <option key={funding.id} value={funding.id}>{funding.name}</option>)}
      </select>
      <button aria-label={`Lançar entrada de ${item.name}`} className={secondaryButtonCls}>Entrada</button>
    </form>
  );
}
