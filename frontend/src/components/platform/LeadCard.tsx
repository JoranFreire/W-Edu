'use client';

import { useState } from 'react';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { leadStatusLabels } from '@/lib/publicSite/leadLabels';
import { formatDateTime } from '@/lib/dates';
import { institutionTypeLabels } from '@/types/institution';
import type { LeadStatus, SalesLead } from '@/types/publicSite';

/** Um interessado: dados de contato, o que pediu, a etapa da negociacao e anotacoes da equipe. */
export default function LeadCard({ lead, onUpdate }: {
  lead: SalesLead;
  onUpdate: (patch: { status?: LeadStatus; notes?: string }) => void;
}) {
  const [notes, setNotes] = useState(lead.notes ?? '');
  return (
    <li className="space-y-3 px-5 py-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="font-semibold text-gray-900 dark:text-white">{lead.institution_name}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {lead.name} · <a href={`mailto:${lead.email}`} className="text-indigo-600 hover:underline">{lead.email}</a>{lead.phone ? ` · ${lead.phone}` : ''}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {institutionTypeLabels[lead.institution_type]}
            {lead.students_estimate ? ` · ~${lead.students_estimate} alunos` : ''}
            {lead.plan_name ? ` · plano ${lead.plan_name}` : ''} · {formatDateTime(lead.created_at)}
          </p>
        </div>
        <select aria-label={`Etapa de ${lead.institution_name}`} value={lead.status} onChange={(e) => onUpdate({ status: e.target.value as LeadStatus })} className={`${inputCls} sm:w-48`}>
          {Object.entries(leadStatusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </div>
      {lead.message && <p className="whitespace-pre-line rounded-lg bg-gray-50 p-3 text-sm text-gray-700 dark:bg-gray-900 dark:text-gray-300">{lead.message}</p>}
      <div className="flex flex-col gap-2 sm:flex-row">
        <input aria-label={`Anotações sobre ${lead.institution_name}`} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Anotações da equipe" className={inputCls} />
        <button type="button" disabled={notes === (lead.notes ?? '')} onClick={() => onUpdate({ notes })} className={`${secondaryButtonCls} shrink-0`}>Salvar anotação</button>
      </div>
    </li>
  );
}
