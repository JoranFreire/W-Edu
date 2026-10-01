'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { PencilSquareIcon } from '@heroicons/react/24/outline';
import ContractTemplateFormModal from '@/components/contracts/ContractTemplateFormModal';
import BackButton from '@/components/common/BackButton';
import SectionHeader from '@/components/common/SectionHeader';
import StatusBadge from '@/components/common/StatusBadge';
import { iconButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { contractKindLabels } from '@/lib/academic/contractLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useContractTemplates } from '@/lib/hooks/contracts/useContractTemplates';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { ContractTemplate, ContractTemplateInput } from '@/types/contracts';

/** Modelos de contrato de matricula e rematricula. */
export default function ContractTemplatesPage() {
  const router = useRouter();
  const { templates, error, save, setActive } = useContractTemplates();
  const [editing, setEditing] = useState<ContractTemplate | 'new' | null>(null);
  useErrorToast(error, 'Erro ao carregar os modelos.');

  const handleSave = async (input: ContractTemplateInput) => {
    await save(editing === 'new' || editing === null ? null : editing.id, input);
    toast.success('Modelo salvo.');
    setEditing(null);
  };
  const toggle = async (template: ContractTemplate) => {
    try {
      await setActive(template.id, !template.is_active);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao atualizar o modelo.'));
    }
  };

  return (
    <div className="space-y-6">
      <BackButton label="Secretaria" onClick={() => router.push('/admin/secretariat')} />
      <section className={`${sectionCls} space-y-4`}>
        <SectionHeader title="Modelos de contrato" description="Texto base dos contratos de matrícula e rematrícula, emitidos pela ficha do aluno." actionLabel="Novo modelo" onAction={() => setEditing('new')} />
        {templates.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum modelo cadastrado.</p> : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {templates.map((template) => (
              <li key={template.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <p className="flex items-center gap-2 font-medium text-gray-900 dark:text-white">
                  {template.name} <span className="text-xs font-normal text-gray-500 dark:text-gray-400">{contractKindLabels[template.kind]}</span>
                  <StatusBadge active={template.is_active} activeLabel="Ativo" inactiveLabel="Inativo" />
                </p>
                <div className="flex items-center gap-2">
                  <button onClick={() => toggle(template)} className={secondaryButtonCls}>{template.is_active ? 'Desativar' : 'Ativar'}</button>
                  <button onClick={() => setEditing(template)} aria-label={`Editar ${template.name}`} className={iconButtonCls}><PencilSquareIcon className="h-4 w-4" /></button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
      {editing && <ContractTemplateFormModal template={editing === 'new' ? undefined : editing} onSave={handleSave} onClose={() => setEditing(null)} />}
    </div>
  );
}
