'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { reaisToCents } from '@/lib/finance/tuitionLabels';
import type { SaasPlanInput } from '@/types/saas';

/** Novo plano do catalogo: nome, preco mensal e limite opcional de alunos ativos. */
export default function SaasPlanForm({ onSubmit }: { onSubmit: (input: SaasPlanInput) => Promise<void> }) {
  const empty = { name: '', price: '', maxStudents: '' };
  const [draft, setDraft] = useState(empty);
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({
        name: draft.name, description: null, monthly_price_cents: reaisToCents(draft.price),
        max_students: draft.maxStudents ? Number(draft.maxStudents) : null,
      });
      setDraft(empty);
      toast.success('Plano criado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao criar o plano.'));
    }
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-4">
      <input required aria-label="Nome do plano" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} placeholder="Nome" className={inputCls} />
      <input required inputMode="decimal" aria-label="Preço mensal" value={draft.price} onChange={(e) => setDraft({ ...draft, price: e.target.value })} placeholder="Preço mensal (R$)" className={inputCls} />
      <input type="number" min={1} aria-label="Limite de alunos" value={draft.maxStudents} onChange={(e) => setDraft({ ...draft, maxStudents: e.target.value })} placeholder="Limite de alunos (vazio: sem limite)" className={inputCls} />
      <button className={primaryButtonCls}>Criar plano</button>
    </form>
  );
}
