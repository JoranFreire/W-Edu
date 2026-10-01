'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { toOptionalInt } from '@/lib/forms/numbers';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { PersonSummary } from '@/types/academicGroups';
import type { InternshipInput } from '@/types/completion';

/** Cadastro do estagio pela secretaria (concedente, orientador, termo e periodo). */
export default function InternshipFormModal({ advisors, onSave, onClose }: {
  advisors: PersonSummary[];
  onSave: (input: InternshipInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState({
    company_name: '', supervisor_name: '', advisor_id: '', is_mandatory: true, agreement_number: '',
    starts_on: '', ends_on: '', planned_hours: '',
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: InternshipInput = {
      company_name: form.company_name, supervisor_name: form.supervisor_name || null, advisor_id: form.advisor_id ? form.advisor_id : null,
      is_mandatory: form.is_mandatory, agreement_number: form.agreement_number || null, starts_on: form.starts_on,
      ends_on: form.ends_on || null, planned_hours: toOptionalInt(form.planned_hours),
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao cadastrar o estágio.')));
  };

  return (
    <Modal title="Novo estágio" size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={labelCls}>Concedente
          <input required value={form.company_name} onChange={(e) => set({ company_name: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Supervisor na concedente
          <input value={form.supervisor_name} onChange={(e) => set({ supervisor_name: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Orientador
          <select value={form.advisor_id} onChange={(e) => set({ advisor_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Sem orientador</option>
            {advisors.map((advisor) => <option key={advisor.id} value={advisor.id}>{advisor.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Termo de compromisso
          <input value={form.agreement_number} onChange={(e) => set({ agreement_number: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Início
          <input required type="date" value={form.starts_on} onChange={(e) => set({ starts_on: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Término previsto
          <input type="date" value={form.ends_on} onChange={(e) => set({ ends_on: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Horas previstas
          <input type="number" min={1} value={form.planned_hours} onChange={(e) => set({ planned_hours: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className="flex items-center gap-2 self-end text-sm text-gray-700 dark:text-gray-300">
          <input type="checkbox" checked={form.is_mandatory} onChange={(e) => set({ is_mandatory: e.target.checked })} />
          Estágio obrigatório (conta para a carga do programa)
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
