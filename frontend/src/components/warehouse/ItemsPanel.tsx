'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { materialKindLabels } from '@/lib/academic/warehouseLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import { reaisToCents } from '@/lib/finance/tuitionLabels';
import { useWarehouseItems } from '@/lib/hooks/warehouse/useWarehouseItems';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { MaterialKind } from '@/types/warehouse';

/** Materiais: cadastro, saldo, emprestados, alerta de minimo e entrada de estoque. */
export default function ItemsPanel() {
  const { items, error, create, receive } = useWarehouseItems();
  const empty = { name: '', category: '', kind: 'consumable' as MaterialKind, unit: 'unidade', minStock: '0', location: '', cost: '' };
  const [draft, setDraft] = useState(empty);
  const [entry, setEntry] = useState<Record<number, string>>({});
  useErrorToast(error, 'Erro ao carregar os materiais.');
  const run = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir.'));
    }
  };
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(async () => {
      await create({ name: draft.name, category: draft.category || null, kind: draft.kind, unit: draft.unit, min_stock: Number(draft.minStock || 0),
        location: draft.location || null, unit_cost_cents: draft.cost ? reaisToCents(draft.cost) : 0 });
      setDraft(empty);
    }, 'Material cadastrado.');
  };
  return (
    <section className={`${sectionCls} space-y-4`}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-7">
        <input required aria-label="Nome do material" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} placeholder="Material" className={`${inputCls} md:col-span-2`} />
        <input aria-label="Categoria" value={draft.category} onChange={(e) => setDraft({ ...draft, category: e.target.value })} placeholder="Categoria" className={inputCls} />
        <select aria-label="Tipo de material" value={draft.kind} onChange={(e) => setDraft({ ...draft, kind: e.target.value as MaterialKind })} className={inputCls}>
          {optionsOf(materialKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <input required aria-label="Unidade do material" value={draft.unit} onChange={(e) => setDraft({ ...draft, unit: e.target.value })} className={inputCls} />
        <input type="number" min={0} aria-label="Estoque mínimo" value={draft.minStock} onChange={(e) => setDraft({ ...draft, minStock: e.target.value })} className={inputCls} />
        <input inputMode="decimal" aria-label="Custo unitário do material" value={draft.cost} onChange={(e) => setDraft({ ...draft, cost: e.target.value })} placeholder="Custo (R$)" className={inputCls} />
        <input aria-label="Local de guarda" value={draft.location} onChange={(e) => setDraft({ ...draft, location: e.target.value })} placeholder="Local (ex.: Armário 2)" className={`${inputCls} md:col-span-6`} />
        <button className={primaryButtonCls}>Cadastrar</button>
      </form>
      <ul className="divide-y divide-gray-100 dark:divide-gray-700">
        {items.map((item) => (
          <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
            <span className="text-gray-800 dark:text-gray-200">
              <strong className="text-gray-900 dark:text-white">{item.name}</strong>
              {item.category ? ` · ${item.category}` : ''} · {materialKindLabels[item.kind]} · {formatMoney(item.unit_cost_cents)}/{item.unit}
              {item.location ? ` · ${item.location}` : ''} ·{' '}
              <span className={item.below_minimum ? 'font-semibold text-red-600' : ''}>{item.available} disponível(is) (mín. {item.min_stock})</span>
              {item.on_loan ? ` · ${item.on_loan} emprestado(s)` : ''}
            </span>
            <span className="flex items-center gap-2">
              <input type="number" min={1} aria-label={`Quantidade recebida de ${item.name}`} value={entry[item.id] ?? ''} onChange={(e) => setEntry({ ...entry, [item.id]: e.target.value })} placeholder="Qtd." className={`${inputCls} w-24`} />
              <button disabled={!entry[item.id]} onClick={() => run(async () => {
                await receive(item.id, { quantity: Number(entry[item.id]), unit_cost_cents: null, origin: 'purchase', funding_source_id: null, received_on: todayIso() });
                setEntry({ ...entry, [item.id]: '' });
              }, 'Entrada registrada.')} aria-label={`Lançar entrada de ${item.name}`} className={secondaryButtonCls}>Entrada</button>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
