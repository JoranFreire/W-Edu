'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { relationshipLabels } from '@/lib/academic/guardianLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import type { GuardianLinkInput } from '@/lib/hooks/secretariat/useGuardianLinks';
import type { GuardianRelationship } from '@/types/guardians';

const empty: GuardianLinkInput = {
  name: '', email: '', password: null, relationship_kind: 'mother', is_financial: false, can_pick_up: true, is_primary: false,
};

/** Vincula responsavel: conta existente pelo e-mail ou nova conta com senha inicial. */
export default function GuardianLinkForm({ onAdd }: { onAdd: (input: GuardianLinkInput) => Promise<void> }) {
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<GuardianLinkInput>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onAdd({ ...draft, password: draft.password || null });
      setDraft(empty);
      toast.success('Responsável vinculado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao vincular responsável.'));
    }
  };

  const flags: { key: 'is_financial' | 'can_pick_up' | 'is_primary'; label: string }[] = [
    { key: 'is_financial', label: 'Responsável financeiro' },
    { key: 'can_pick_up', label: 'Autorizado a retirar' },
    { key: 'is_primary', label: 'Contato principal' },
  ];

  return (
    <form onSubmit={submit} className="space-y-3">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <input required aria-label="Nome do responsável" value={draft.name} onChange={(e) => set({ name: e.target.value })} placeholder="Nome" className={inputCls} />
        <input required type="email" aria-label="E-mail do responsável" value={draft.email} onChange={(e) => set({ email: e.target.value })} placeholder="E-mail" className={inputCls} />
        <input type="password" aria-label="Senha inicial" value={draft.password ?? ''} onChange={(e) => set({ password: e.target.value })} placeholder="Senha inicial (nova conta)" className={inputCls} />
        <select aria-label="Parentesco" value={draft.relationship_kind} onChange={(e) => set({ relationship_kind: e.target.value as GuardianRelationship })} className={inputCls}>
          {optionsOf(relationshipLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
      <div className="flex flex-wrap items-center gap-4">
        {flags.map((flag) => (
          <label key={flag.key} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input type="checkbox" checked={draft[flag.key]} onChange={(e) => set({ [flag.key]: e.target.checked })} className="h-4 w-4 rounded border-gray-300" />
            {flag.label}
          </label>
        ))}
        <button className={`${primaryButtonCls} ml-auto`}>Vincular</button>
      </div>
    </form>
  );
}
