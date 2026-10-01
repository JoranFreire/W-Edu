'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, labelCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { MaterialRequestInput, WarehouseItem } from '@/types/warehouse';

interface LineDraft { itemId: string; quantity: string }

/** Nova requisicao: finalidade, data de uso, turma (opcional) e materiais com quantidade. */
export default function MaterialRequestForm({ items, offerings, onSubmit }: {
  items: WarehouseItem[];
  offerings: { id: number; name: string }[];
  onSubmit: (input: MaterialRequestInput) => Promise<void>;
}) {
  const empty = { purpose: '', neededOn: '', offeringId: '', lines: [{ itemId: '', quantity: '1' }] as LineDraft[] };
  const [draft, setDraft] = useState(empty);
  const setLine = (index: number, patch: Partial<LineDraft>) =>
    setDraft({ ...draft, lines: draft.lines.map((line, i) => (i === index ? { ...line, ...patch } : line)) });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({
        purpose: draft.purpose, needed_on: draft.neededOn, class_offering_id: draft.offeringId ? Number(draft.offeringId) : null,
        lines: draft.lines.filter((line) => line.itemId).map((line) => ({ item_id: Number(line.itemId), quantity: Number(line.quantity) })),
      });
      setDraft(empty);
      toast.success('Requisição enviada para aprovação.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao enviar a requisição.'));
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <label className={labelCls}>Finalidade<input required value={draft.purpose} onChange={(e) => setDraft({ ...draft, purpose: e.target.value })} placeholder="Ex.: atividade de pintura" className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Data de uso<input required type="date" value={draft.neededOn} onChange={(e) => setDraft({ ...draft, neededOn: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Turma (opcional)
          <select value={draft.offeringId} onChange={(e) => setDraft({ ...draft, offeringId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Sem turma</option>
            {offerings.map((offering) => <option key={offering.id} value={offering.id}>{offering.name}</option>)}
          </select>
        </label>
      </div>
      {draft.lines.map((line, index) => (
        <div key={index} className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <select aria-label={`Material ${index + 1}`} value={line.itemId} onChange={(e) => setLine(index, { itemId: e.target.value })} className={`${inputCls} md:col-span-3`}>
            <option value="">Material…</option>
            {items.map((item) => <option key={item.id} value={item.id}>{item.name} ({item.available} {item.unit} disponível(is))</option>)}
          </select>
          <input type="number" min={1} aria-label={`Quantidade ${index + 1}`} value={line.quantity} onChange={(e) => setLine(index, { quantity: e.target.value })} className={inputCls} />
        </div>
      ))}
      <div className="flex justify-between">
        <button type="button" onClick={() => setDraft({ ...draft, lines: [...draft.lines, { itemId: '', quantity: '1' }] })} className={secondaryButtonCls}>Adicionar material</button>
        <button className={primaryButtonCls}>Enviar requisição</button>
      </div>
    </form>
  );
}
