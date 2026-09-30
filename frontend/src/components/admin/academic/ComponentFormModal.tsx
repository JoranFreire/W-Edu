'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { componentKindLabels, optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { fromOptionalInt, toOptionalInt } from '@/lib/forms/numbers';
import type { ComponentInput } from '@/lib/hooks/admin/academic/useCurriculumDetail';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { ComponentKind, CurriculumComponent, Subject } from '@/types/academic';

/** Inclui uma disciplina na matriz ou edita periodo/tipo/carga de um componente. */
export default function ComponentFormModal({ component, subjects, termLabel, defaultTerm, onSave, onClose }: {
  component?: CurriculumComponent;
  subjects: Subject[];
  termLabel: string;
  defaultTerm: number;
  onSave: (input: ComponentInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState({
    subject_id: component?.subject.id ?? 0,
    term_number: String(component?.term_number ?? defaultTerm),
    kind: component?.kind ?? ('mandatory' as ComponentKind),
    hours: fromOptionalInt(component?.hours_override),
    credits: fromOptionalInt(component?.credits_override),
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: ComponentInput = {
      subject_id: form.subject_id,
      term_number: toOptionalInt(form.term_number) ?? 1,
      kind: form.kind,
      hours: toOptionalInt(form.hours),
      credits: toOptionalInt(form.credits),
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar componente.')));
  };

  return (
    <Modal title={component ? `${component.subject.code} · ${component.subject.name}` : 'Incluir na matriz'} size="md" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {!component && (
          <label className={`${labelCls} sm:col-span-2`}>Disciplina
            <select required value={form.subject_id || ''} onChange={(e) => set({ subject_id: Number(e.target.value) })} className={`mt-1 ${inputCls}`}>
              <option value="">Selecione...</option>
              {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.code} · {subject.name}</option>)}
            </select>
          </label>
        )}
        <label className={labelCls}>{termLabel}
          <input type="number" min={1} required value={form.term_number} onChange={(e) => set({ term_number: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Tipo
          <select value={form.kind} onChange={(e) => set({ kind: e.target.value as ComponentKind })} className={`mt-1 ${inputCls}`}>
            {optionsOf(componentKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Carga horária (opcional)
          <input type="number" min={0} value={form.hours} onChange={(e) => set({ hours: e.target.value })} placeholder="Da disciplina" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Créditos (opcional)
          <input type="number" min={0} value={form.credits} onChange={(e) => set({ credits: e.target.value })} placeholder="Da disciplina" className={`mt-1 ${inputCls}`} />
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
