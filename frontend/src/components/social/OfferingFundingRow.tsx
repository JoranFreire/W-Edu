'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { ClassOffering } from '@/types/schedule';
import type { FundingSource } from '@/types/socialPrograms';

/** Financiador da turma e limite de faltas que desliga o aluno. */
export default function OfferingFundingRow({ offering, fundingSources, onSave }: {
  offering: ClassOffering;
  fundingSources: FundingSource[];
  onSave: (fundingId: number | null, limit: number | null) => Promise<void>;
}) {
  const [fundingId, setFundingId] = useState(String(offering.funding_source_id ?? ''));
  const [limit, setLimit] = useState(String(offering.max_absence_percent ?? ''));
  const save = async () => {
    try {
      await onSave(fundingId ? Number(fundingId) : null, limit ? Number(limit) : null);
      toast.success('Turma atualizada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao atualizar a turma.'));
    }
  };
  return (
    <li className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
      <span className="font-medium text-gray-900 dark:text-white">{offering.name}</span>
      <span className="flex flex-wrap items-center gap-2">
        <select aria-label={`Financiador da turma ${offering.name}`} value={fundingId} onChange={(e) => setFundingId(e.target.value)} className={`${inputCls} w-56`}>
          <option value="">Sem financiador</option>
          {fundingSources.map((funding) => <option key={funding.id} value={funding.id}>{funding.name}</option>)}
        </select>
        <input type="number" min={1} max={100} aria-label={`Limite de faltas da turma ${offering.name}`} value={limit} onChange={(e) => setLimit(e.target.value)} placeholder="Faltas máx. (%)" className={`${inputCls} w-36`} />
        <button onClick={save} aria-label={`Salvar turma ${offering.name}`} className={secondaryButtonCls}>Salvar</button>
      </span>
    </li>
  );
}
