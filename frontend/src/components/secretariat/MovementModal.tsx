'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSubmitting } from '@/lib/hooks/useSubmitting';

export interface MovementField {
  name: string;
  label: string;
  options?: { value: string; label: string }[];
  required?: boolean;
}

/** Formulario de uma movimentacao: campos proprios (destino, programa, periodo...) e justificativa. */
export default function MovementModal({ title, fields, onSubmit, onClose }: {
  title: string;
  fields: MovementField[];
  onSubmit: (values: Record<string, string>) => Promise<void>;
  onClose: () => void;
}) {
  const [values, setValues] = useState<Record<string, string>>({});
  const { saving, run } = useSubmitting();

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSubmit(values)).catch((error) => toast.error(apiErrorMessage(error, 'Não foi possível registrar a movimentação.')));
  };

  return (
    <Modal title={title} size="md" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        {fields.map((field) => (
          <label key={field.name} className={labelCls}>{field.label}
            {field.options ? (
              <select required={field.required} value={values[field.name] ?? ''} onChange={(e) => setValues({ ...values, [field.name]: e.target.value })} className={`mt-1 ${inputCls}`}>
                <option value="">Selecione...</option>
                {field.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            ) : (
              <input required={field.required} value={values[field.name] ?? ''} onChange={(e) => setValues({ ...values, [field.name]: e.target.value })} className={`mt-1 ${inputCls}`} />
            )}
          </label>
        ))}
        <label className={labelCls}>Justificativa
          <textarea rows={3} value={values.reason ?? ''} onChange={(e) => setValues({ ...values, reason: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <FormActions saving={saving} onCancel={onClose} submitLabel="Confirmar" />
      </form>
    </Modal>
  );
}
