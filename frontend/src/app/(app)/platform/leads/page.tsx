'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { InboxArrowDownIcon } from '@heroicons/react/24/outline';
import { inputCls } from '@/components/common/formStyles';
import Spinner from '@/components/common/Spinner';
import LeadCard from '@/components/platform/LeadCard';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSalesLeads } from '@/lib/hooks/platform/useSalesLeads';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { leadStatusLabels } from '@/lib/publicSite/leadLabels';
import type { LeadStatus, SalesLead } from '@/types/publicSite';

/** Interessados em contratar a plataforma, vindos do formulario da pagina de contratacao. */
export default function PlatformLeadsPage() {
  const [status, setStatus] = useState<LeadStatus | ''>('');
  const { leads, loading, error, update } = useSalesLeads(status);
  useErrorToast(error, 'Erro ao carregar interessados.');

  const save = (lead: SalesLead, patch: { status?: LeadStatus; notes?: string }) =>
    update(lead, patch).then(() => toast.success('Interessado atualizado.')).catch((e) => toast.error(apiErrorMessage(e, 'Erro ao atualizar.')));

  return (
    <div className="max-w-5xl space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900 dark:text-white"><InboxArrowDownIcon className="h-6 w-6 text-indigo-600" />Interessados</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Pedidos de contato e demonstração vindos da página de contratação.</p>
        </div>
        <select aria-label="Filtrar por etapa" value={status} onChange={(e) => setStatus(e.target.value as LeadStatus | '')} className={`${inputCls} sm:w-56`}>
          <option value="">Todas as etapas</option>
          {Object.entries(leadStatusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </div>
      {loading && leads.length === 0 ? <Spinner /> : leads.length === 0 ? (
        <p className="rounded-xl border border-dashed border-gray-300 p-8 text-center text-sm text-gray-500 dark:border-gray-600 dark:text-gray-400">Nenhum interessado{status ? ' nesta etapa' : ''}.</p>
      ) : (
        <ul aria-label="Interessados" className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white dark:divide-gray-700 dark:border-gray-700 dark:bg-gray-800">
          {leads.map((lead) => <LeadCard key={`${lead.id}-${lead.notes ?? ''}`} lead={lead} onUpdate={(patch) => save(lead, patch)} />)}
        </ul>
      )}
    </div>
  );
}
