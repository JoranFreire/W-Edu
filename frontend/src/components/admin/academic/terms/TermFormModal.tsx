'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { optionsOf, termKindLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import type { AcademicTermInput } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { AcademicTerm, TermKind } from '@/types/academicCalendar';

export default function TermFormModal({ term, onSave, onClose }: {
  term?: AcademicTerm;
  onSave: (input: AcademicTermInput) => Promise<void>;
  onClose: () => void;
}) {
  const terms = useTerminology();
  const [form, setForm] = useState<AcademicTermInput>({
    name: term?.name ?? '',
    kind: term?.kind ?? 'semester',
    starts_on: term?.starts_on ?? '',
    ends_on: term?.ends_on ?? '',
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<AcademicTermInput>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave(form)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar período.')));
  };

  return (
    <Modal title={term ? `Editar: ${term.name}` : terms.newAcademicTerm} size="md" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={labelCls}>Nome
          <input required value={form.name} onChange={(e) => set({ name: e.target.value })} placeholder="Ex.: 2027 ou 2027.1" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Regime
          <select value={form.kind} onChange={(e) => set({ kind: e.target.value as TermKind })} className={`mt-1 ${inputCls}`}>
            {optionsOf(termKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Início
          <input type="date" required value={form.starts_on} onChange={(e) => set({ starts_on: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Fim
          <input type="date" required value={form.ends_on} onChange={(e) => set({ ends_on: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
