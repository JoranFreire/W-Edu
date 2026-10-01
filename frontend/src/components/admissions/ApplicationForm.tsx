'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, labelCls, primaryButtonCls } from '@/components/common/formStyles';
import { schoolingLabels } from '@/lib/academic/admissionLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { reaisToCents } from '@/lib/finance/tuitionLabels';
import type { NewAccount } from '@/lib/hooks/admissions/useApplicationSubmit';
import type { AdmissionCall, ApplicationAnswers, Schooling } from '@/types/admissions';

/** Questionario socioeconomico e, para quem nao tem conta, os dados de acesso. */
export default function ApplicationForm({ call, needsAccount, onSubmit }: {
  call: AdmissionCall;
  needsAccount: boolean;
  onSubmit: (answers: ApplicationAnswers, account: NewAccount | null) => Promise<void>;
}) {
  const [account, setAccount] = useState<NewAccount>({ name: '', email: '', password: '' });
  const [draft, setDraft] = useState({ birthDate: '', schooling: 'high_school' as Schooling, income: '', household: '1', city: '', reserved: false });
  const [sending, setSending] = useState(false);
  const set = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSending(true);
    try {
      await onSubmit({
        birth_date: draft.birthDate, schooling: draft.schooling, family_income_cents: reaisToCents(draft.income || '0'),
        household_size: Number(draft.household), city: draft.city, claims_reserved: draft.reserved,
      }, needsAccount ? account : null);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Não foi possível concluir a inscrição.'));
    } finally {
      setSending(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      {needsAccount && (
        <fieldset className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <legend className="mb-2 text-sm font-semibold text-gray-900 dark:text-white">Seus dados de acesso</legend>
          <label className={labelCls}>Nome completo<input required value={account.name} onChange={(e) => setAccount({ ...account, name: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
          <label className={labelCls}>E-mail<input required type="email" value={account.email} onChange={(e) => setAccount({ ...account, email: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
          <label className={labelCls}>Senha<input required type="password" minLength={6} value={account.password} onChange={(e) => setAccount({ ...account, password: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        </fieldset>
      )}
      <fieldset className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <legend className="mb-2 text-sm font-semibold text-gray-900 dark:text-white">Questionário</legend>
        <label className={labelCls}>Data de nascimento<input required type="date" value={draft.birthDate} onChange={(e) => set({ birthDate: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Escolaridade
          <select value={draft.schooling} onChange={(e) => set({ schooling: e.target.value as Schooling })} className={`mt-1 ${inputCls}`}>
            {optionsOf(schoolingLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Cidade onde mora<input required value={draft.city} onChange={(e) => set({ city: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Renda total da família (R$/mês)<input required inputMode="decimal" value={draft.income} onChange={(e) => set({ income: e.target.value })} placeholder="0,00" className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Pessoas na família<input required type="number" min={1} max={30} value={draft.household} onChange={(e) => set({ household: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        {call.reserved_seats > 0 && (
          <label className="flex items-center gap-2 self-end text-sm text-gray-700 dark:text-gray-300">
            <input type="checkbox" checked={draft.reserved} onChange={(e) => set({ reserved: e.target.checked })} />
            Concorrer às vagas reservadas ({call.reserved_label ?? 'reserva'})
          </label>
        )}
      </fieldset>
      <button disabled={sending} className={primaryButtonCls}>{sending ? 'Enviando...' : 'Confirmar inscrição'}</button>
    </form>
  );
}
