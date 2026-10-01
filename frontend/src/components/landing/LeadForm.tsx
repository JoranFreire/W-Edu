'use client';

import { useSearchParams } from 'next/navigation';
import { inputCls, labelCls, primaryButtonCls } from '@/components/common/formStyles';
import { useLeadForm } from '@/lib/publicSite/useLeadForm';
import { type InstitutionType, institutionTypeLabels } from '@/types/institution';
import type { PublicPlan } from '@/types/publicSite';

/** Formulario de interesse: chega a administracao da plataforma (Interessados). */
export default function LeadForm({ plans }: { plans: PublicPlan[] }) {
  const chosenPlan = useSearchParams().get('plano') ?? '';
  const { draft, set, state, submit } = useLeadForm(plans.some((plan) => plan.id === chosenPlan) ? chosenPlan : '');

  if (state === 'sent') {
    return (
      <div role="status" className="rounded-xl bg-emerald-50 p-6 text-emerald-800 ring-1 ring-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-200 dark:ring-emerald-800">
        <p className="font-semibold">Recebemos seu interesse!</p>
        <p className="mt-1 text-sm">Nossa equipe vai entrar em contato pelo e-mail ou telefone informados.</p>
      </div>
    );
  }

  return (
    <form onSubmit={(event) => { event.preventDefault(); submit(); }} className="grid gap-4 sm:grid-cols-2">
      <label className={labelCls}>Seu nome *<input required minLength={2} value={draft.name} onChange={(e) => set({ name: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
      <label className={labelCls}>E-mail *<input required type="email" value={draft.email} onChange={(e) => set({ email: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
      <label className={labelCls}>Telefone / WhatsApp<input value={draft.phone} onChange={(e) => set({ phone: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
      <label className={labelCls}>Instituição *<input required minLength={2} value={draft.institutionName} onChange={(e) => set({ institutionName: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
      <label className={labelCls}>Tipo de instituição
        <select value={draft.institutionType} onChange={(e) => set({ institutionType: e.target.value as InstitutionType })} className={`mt-1 ${inputCls}`}>
          {Object.entries(institutionTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </label>
      <label className={labelCls}>Quantos alunos, aproximadamente?<input type="number" min={0} value={draft.students} onChange={(e) => set({ students: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
      {plans.length > 0 && (
        <label className={`${labelCls} sm:col-span-2`}>Plano de interesse
          <select value={draft.planId} onChange={(e) => set({ planId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Ainda não sei</option>
            {plans.map((plan) => <option key={plan.id} value={plan.id}>{plan.name}</option>)}
          </select>
        </label>
      )}
      <label className={`${labelCls} sm:col-span-2`}>Mensagem<textarea rows={4} value={draft.message} onChange={(e) => set({ message: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
      {/* Campo-armadilha: escondido de pessoas; robos que o preenchem sao descartados no servidor. */}
      <input type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" value={draft.website} onChange={(e) => set({ website: e.target.value })} className="hidden" />
      {state === 'error' && <p role="alert" className="text-sm text-red-600 sm:col-span-2">Não foi possível enviar agora. Tente de novo em instantes.</p>}
      <div className="sm:col-span-2">
        <button type="submit" disabled={state === 'sending'} className={`${primaryButtonCls} w-full sm:w-auto`}>{state === 'sending' ? 'Enviando...' : 'Quero conversar'}</button>
      </div>
    </form>
  );
}
