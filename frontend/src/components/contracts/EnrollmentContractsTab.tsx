'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useContractTemplates } from '@/lib/hooks/contracts/useContractTemplates';
import { useEnrollmentContracts } from '@/lib/hooks/contracts/useEnrollmentContracts';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Contract } from '@/types/contracts';
import ContractCard from './ContractCard';

/** Aba Contratos da ficha: emissao a partir de um modelo, download e cancelamento. */
export default function EnrollmentContractsTab({ enrollmentId }: { enrollmentId: string }) {
  const { contracts, error, issue, cancel, download } = useEnrollmentContracts(enrollmentId);
  const { templates } = useContractTemplates();
  const { terms } = useAcademicTerms();
  const [draft, setDraft] = useState({ templateId: '', termId: '' });
  useErrorToast(error, 'Erro ao carregar os contratos.');

  const run = async (action: () => Promise<void>, success: string, fallback: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, fallback));
    }
  };
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => issue(draft.templateId, draft.termId ? draft.termId : null), 'Contrato emitido.', 'Erro ao emitir o contrato.');
  };
  const handleCancel = (contract: Contract) => {
    if (!globalThis.confirm(`Cancelar ${contract.title}?`)) return;
    run(() => cancel(contract.id), 'Contrato cancelado.', 'Erro ao cancelar.');
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Contratos</h2>
      <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <select required aria-label="Modelo de contrato" value={draft.templateId} onChange={(e) => setDraft({ ...draft, templateId: e.target.value })} className={inputCls}>
          <option value="">Modelo…</option>
          {templates.filter((template) => template.is_active).map((template) => <option key={template.id} value={template.id}>{template.name}</option>)}
        </select>
        <select aria-label="Período do contrato" value={draft.termId} onChange={(e) => setDraft({ ...draft, termId: e.target.value })} className={inputCls}>
          <option value="">Sem período</option>
          {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
        </select>
        <button className={primaryButtonCls}>Emitir contrato</button>
      </form>
      {contracts.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum contrato emitido.</p> : (
        <ul className="space-y-3">
          {contracts.map((contract) => (
            <ContractCard key={contract.id} contract={contract}>
              <button onClick={() => run(() => download(contract), 'Download iniciado.', 'Erro ao baixar.')} className={secondaryButtonCls}>PDF</button>
              {contract.status === 'pending' && (
                <button onClick={() => handleCancel(contract)} aria-label={`Cancelar ${contract.title}`} className={secondaryButtonCls}>Cancelar</button>
              )}
            </ContractCard>
          ))}
        </ul>
      )}
    </section>
  );
}
