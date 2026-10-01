'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { subscriptionStatusLabels } from '@/lib/platform/saasLabels';
import type { InstitutionSubscription, SaasPlan, SaasSubscriptionStatus, SubscriptionInput } from '@/types/saas';

/** Atribui ou troca o plano da instituicao (o pai remonta com `key` quando a assinatura muda). */
export default function SubscriptionForm({ subscription, plans, onSubmit }: {
  subscription: InstitutionSubscription | null;
  plans: SaasPlan[];
  onSubmit: (input: SubscriptionInput) => Promise<void>;
}) {
  const [draft, setDraft] = useState({
    planId: String(subscription?.plan.id ?? ''), status: subscription?.status ?? ('trial' as SaasSubscriptionStatus), trialEndsOn: subscription?.trial_ends_on ?? '',
  });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({ plan_id: draft.planId, status: draft.status, trial_ends_on: draft.status === 'trial' && draft.trialEndsOn ? draft.trialEndsOn : null });
      toast.success('Plano atualizado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao atualizar o plano.'));
    }
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-4">
      <select required aria-label="Plano da instituição" value={draft.planId} onChange={(e) => setDraft({ ...draft, planId: e.target.value })} className={inputCls}>
        <option value="">Plano…</option>
        {plans.filter((plan) => plan.is_active).map((plan) => <option key={plan.id} value={plan.id}>{plan.name}</option>)}
      </select>
      <select aria-label="Situação da assinatura" value={draft.status} onChange={(e) => setDraft({ ...draft, status: e.target.value as SaasSubscriptionStatus })} className={inputCls}>
        {optionsOf(subscriptionStatusLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      <input type="date" aria-label="Fim do teste" disabled={draft.status !== 'trial'} value={draft.trialEndsOn} onChange={(e) => setDraft({ ...draft, trialEndsOn: e.target.value })} className={inputCls} />
      <button className={primaryButtonCls}>Salvar plano</button>
    </form>
  );
}
