'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { CurriculumInput } from '@/lib/hooks/admin/academic/useCurricula';
import { useSubmitting } from '@/lib/hooks/useSubmitting';

/** Cria uma matriz vazia ou uma nova versao copiada de `sourceVersion`. */
export default function CurriculumVersionModal({ sourceVersion, onSave, onClose }: {
  sourceVersion?: string;
  onSave: (input: CurriculumInput) => Promise<void>;
  onClose: () => void;
}) {
  const [version, setVersion] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const { saving, run } = useSubmitting();

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave({ version, valid_from: validFrom || null }))
      .catch((error) => toast.error(apiErrorMessage(error, 'Erro ao criar matriz.')));
  };

  return (
    <Modal
      title={sourceVersion ? 'Nova versão da matriz' : 'Nova matriz curricular'}
      description={sourceVersion ? `Copia os componentes da versão ${sourceVersion} para um novo rascunho.` : undefined}
      size="sm"
      onClose={onClose}
    >
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Versão
          <input required value={version} onChange={(e) => setVersion(e.target.value)} placeholder="Ex.: 2027" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Vigente a partir de
          <input type="date" value={validFrom} onChange={(e) => setValidFrom(e.target.value)} className={`mt-1 ${inputCls}`} />
        </label>
        <FormActions saving={saving} onCancel={onClose} submitLabel="Criar" />
      </form>
    </Modal>
  );
}
