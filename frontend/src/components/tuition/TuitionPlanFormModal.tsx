'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { reaisToCents, tuitionBasisLabels } from '@/lib/finance/tuitionLabels';
import { useClassGroups } from '@/lib/hooks/admin/academic/useClassGroups';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { Program } from '@/types/academic';
import type { AcademicTerm } from '@/types/academicCalendar';
import type { TuitionBasis, TuitionPlanInput } from '@/types/tuition';

/** Novo plano de mensalidade: base (programa, turma-grupo ou credito), periodo, valor e parcelas. */
export default function TuitionPlanFormModal({ terms, programs, onSave, onClose }: {
  terms: AcademicTerm[];
  programs: Program[];
  onSave: (input: TuitionPlanInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState({
    name: '', basis: 'program' as TuitionBasis, termId: '', programId: '', groupId: '', amount: '', installments: '12', firstDueOn: '',
  });
  const { groups } = useClassGroups(form.termId ? Number(form.termId) : undefined);
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: TuitionPlanInput = {
      name: form.name, basis: form.basis, term_id: Number(form.termId),
      program_id: form.basis !== 'class_group' && form.programId ? Number(form.programId) : null,
      class_group_id: form.basis === 'class_group' && form.groupId ? Number(form.groupId) : null,
      amount_cents: reaisToCents(form.amount), installments: Number(form.installments), first_due_on: form.firstDueOn,
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar o plano.')));
  };

  return (
    <Modal title="Novo plano de mensalidade" size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={`${labelCls} sm:col-span-2`}>Nome
          <input required value={form.name} onChange={(e) => set({ name: e.target.value })} placeholder="Ex.: Mensalidade 2027" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Base de cobrança
          <select value={form.basis} onChange={(e) => set({ basis: e.target.value as TuitionBasis })} className={`mt-1 ${inputCls}`}>
            {optionsOf(tuitionBasisLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Período letivo
          <select required value={form.termId} onChange={(e) => set({ termId: e.target.value, groupId: '' })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione…</option>
            {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
          </select>
        </label>
        {form.basis === 'class_group' ? (
          <label className={labelCls}>Turma-grupo
            <select required value={form.groupId} onChange={(e) => set({ groupId: e.target.value })} className={`mt-1 ${inputCls}`}>
              <option value="">Selecione…</option>
              {groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}
            </select>
          </label>
        ) : (
          <label className={labelCls}>Programa
            <select required={form.basis === 'program'} value={form.programId} onChange={(e) => set({ programId: e.target.value })} className={`mt-1 ${inputCls}`}>
              <option value="">{form.basis === 'credit' ? 'Todos os programas' : 'Selecione…'}</option>
              {programs.map((program) => <option key={program.id} value={program.id}>{program.code} · {program.name}</option>)}
            </select>
          </label>
        )}
        <label className={labelCls}>{form.basis === 'credit' ? 'Valor por crédito (R$)' : 'Valor da parcela (R$)'}
          <input required inputMode="decimal" value={form.amount} onChange={(e) => set({ amount: e.target.value })} placeholder="0,00" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Parcelas
          <input required type="number" min={1} max={24} value={form.installments} onChange={(e) => set({ installments: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Primeiro vencimento
          <input required type="date" value={form.firstDueOn} onChange={(e) => set({ firstDueOn: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
