'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import CertificateRuleForm from '@/components/admin/CertificateRuleForm';
import type { CertificateRule } from '@/types/certificate';

/** Edita a regra do curso a partir do valor salvo; mantem o rascunho ate salvar. */
export default function CertificateRuleEditor({ savedRule, onSave }: {
  savedRule: CertificateRule;
  onSave: (rule: CertificateRule) => Promise<CertificateRule>;
}) {
  const [draft, setDraft] = useState(savedRule);

  const save = async () => {
    try {
      setDraft(await onSave(draft));
      toast.success('Regra atualizada.');
    } catch { toast.error('Erro ao salvar regra.'); }
  };

  return <CertificateRuleForm rule={draft} onChange={setDraft} onSave={save} />;
}
