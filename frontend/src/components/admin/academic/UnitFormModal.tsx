'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { optionsOf, unitKindLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import type { AcademicUnitInput } from '@/lib/hooks/admin/academic/useAcademicUnits';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { AcademicUnit } from '@/types/academic';

export default function UnitFormModal({ unit, units, onSave, onClose }: {
  unit?: AcademicUnit;
  units: AcademicUnit[];
  onSave: (input: AcademicUnitInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState<AcademicUnitInput>({
    name: unit?.name ?? '',
    kind: unit?.kind ?? 'segment',
    parent_id: unit?.parent_id ?? null,
  });
  const { saving, run } = useSubmitting();
  const parents = units.filter((candidate) => candidate.id !== unit?.id);

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave(form)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar unidade.')));
  };

  return (
    <Modal title={unit ? 'Editar unidade' : 'Nova unidade acadêmica'} size="sm" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Nome
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Tipo
          <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value as AcademicUnitInput['kind'] })} className={`mt-1 ${inputCls}`}>
            {optionsOf(unitKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Unidade superior
          <select
            value={form.parent_id ?? ''}
            onChange={(e) => setForm({ ...form, parent_id: e.target.value || null })}
            className={`mt-1 ${inputCls}`}
          >
            <option value="">Nenhuma</option>
            {parents.map((parent) => <option key={parent.id} value={parent.id}>{parent.name}</option>)}
          </select>
        </label>
        <FormActions saving={saving} onCancel={onClose} />
      </form>
    </Modal>
  );
}
