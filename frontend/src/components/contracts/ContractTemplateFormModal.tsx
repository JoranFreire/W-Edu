'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { contractFields, contractKindLabels } from '@/lib/academic/contractLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { ContractKind, ContractTemplate, ContractTemplateInput } from '@/types/contracts';

/** Cria ou edita o texto do modelo; os campos entre chaves sao preenchidos na emissao. */
export default function ContractTemplateFormModal({ template, onSave, onClose }: {
  template?: ContractTemplate;
  onSave: (input: ContractTemplateInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState<ContractTemplateInput>({
    name: template?.name ?? '', kind: template?.kind ?? 'enrollment', body: template?.body ?? '',
  });
  const { saving, run } = useSubmitting();
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave(form)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar o modelo.')));
  };
  return (
    <Modal title={template ? `Editar: ${template.name}` : 'Novo modelo de contrato'} size="xl" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className={labelCls}>Nome
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className={`mt-1 ${inputCls}`} />
          </label>
          <label className={labelCls}>Tipo
            <select disabled={!!template} value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value as ContractKind })} className={`mt-1 ${inputCls}`}>
              {optionsOf(contractKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
        </div>
        <label className={labelCls}>Texto do contrato
          <textarea required rows={12} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} className={`mt-1 font-mono ${inputCls}`} />
        </label>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Campos: {contractFields.map((field) => `{${field.key}} (${field.label})`).join(', ')}. Separe as cláusulas com uma linha em branco.
        </p>
        <FormActions saving={saving} onCancel={onClose} />
      </form>
    </Modal>
  );
}
