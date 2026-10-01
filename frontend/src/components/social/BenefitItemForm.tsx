'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { benefitKindLabels } from '@/lib/academic/socialLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { reaisToCents } from '@/lib/finance/tuitionLabels';
import type { BenefitItemInput, BenefitKind } from '@/types/socialPrograms';

/** Novo item do programa (lanche, kit, uniforme...); lanche costuma valer so para presentes. */
export default function BenefitItemForm({ onSubmit }: { onSubmit: (input: BenefitItemInput) => Promise<void> }) {
  const empty = { name: '', kind: 'snack' as BenefitKind, unit: 'unidade', cost: '', presentOnly: true };
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({ name: draft.name, kind: draft.kind, unit: draft.unit, unit_cost_cents: draft.cost ? reaisToCents(draft.cost) : 0, requires_attendance: draft.presentOnly });
      setDraft(empty);
      toast.success('Item cadastrado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao cadastrar o item.'));
    }
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-6">
      <input required aria-label="Nome do item" value={draft.name} onChange={(e) => set({ name: e.target.value })} placeholder="Item" className={`${inputCls} md:col-span-2`} />
      <select aria-label="Tipo do item" value={draft.kind} onChange={(e) => set({ kind: e.target.value as BenefitKind, presentOnly: e.target.value === 'snack' })} className={inputCls}>
        {optionsOf(benefitKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      <input required aria-label="Unidade do item" value={draft.unit} onChange={(e) => set({ unit: e.target.value })} className={inputCls} />
      <input inputMode="decimal" aria-label="Custo unitário" value={draft.cost} onChange={(e) => set({ cost: e.target.value })} placeholder="Custo (R$)" className={inputCls} />
      <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
        <input type="checkbox" checked={draft.presentOnly} onChange={(e) => set({ presentOnly: e.target.checked })} /> Só para presentes
      </label>
      <div className="md:col-span-6 flex justify-end"><button className={primaryButtonCls}>Cadastrar item</button></div>
    </form>
  );
}
