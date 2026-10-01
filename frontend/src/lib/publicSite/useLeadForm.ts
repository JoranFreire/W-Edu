'use client';

import { useState } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import type { InstitutionType } from '@/types/institution';
import type { SalesLeadInput } from '@/types/publicSite';

export interface LeadDraft {
  name: string;
  email: string;
  phone: string;
  institutionName: string;
  institutionType: InstitutionType;
  students: string;
  planId: string;
  message: string;
  website: string;
}

const EMPTY: Omit<LeadDraft, 'planId'> = {
  name: '', email: '', phone: '', institutionName: '', institutionType: 'school', students: '', message: '', website: '',
};

/** Rascunho e envio do formulario de interesse da pagina de contratacao. */
export function useLeadForm(initialPlanId: string) {
  const [draft, setDraft] = useState<LeadDraft>({ ...EMPTY, planId: initialPlanId });
  const [state, setState] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const set = (patch: Partial<LeadDraft>) => setDraft((current) => ({ ...current, ...patch }));

  const submit = async () => {
    setState('sending');
    const input: SalesLeadInput = {
      name: draft.name, email: draft.email, phone: draft.phone || null, institution_name: draft.institutionName,
      institution_type: draft.institutionType, students_estimate: draft.students ? Number(draft.students) : null,
      plan_id: draft.planId || null, message: draft.message || null, website: draft.website,
    };
    try {
      await api.post(endpoints.publicSite.leads, input);
      setState('sent');
    } catch {
      setState('error');
    }
  };

  return { draft, set, state, submit };
}
