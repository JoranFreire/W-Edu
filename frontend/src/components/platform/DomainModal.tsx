'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { Institution } from '@/types/institution';

/** Dominio proprio da instituicao: o endereco dela passa a mostrar a pagina publica e o acesso ao sistema. */
export default function DomainModal({ institution, onSave, onClose }: {
  institution: Institution;
  onSave: (domain: string) => Promise<void>;
  onClose: () => void;
}) {
  const [domain, setDomain] = useState(institution.custom_domain ?? '');
  const { saving, run } = useSubmitting();

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave(domain.trim())).then(() => { toast.success(domain.trim() ? 'Domínio salvo.' : 'Domínio removido.'); onClose(); })
      .catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar o domínio.')));
  };

  return (
    <Modal title={`Domínio de ${institution.name}`} description="Endereço próprio do cliente, como escola.com.br. Deixe vazio para remover." onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Domínio
          <input value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="escola.com.br" className={`mt-1 ${inputCls}`} />
        </label>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          O cliente aponta o domínio (registro CNAME ou A) para o servidor da plataforma; o certificado HTTPS é emitido no proxy.
        </p>
        <FormActions saving={saving} onCancel={onClose} />
      </form>
    </Modal>
  );
}
