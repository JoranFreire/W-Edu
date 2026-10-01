'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ContractTemplate, ContractTemplateInput } from '@/types/contracts';

/** Modelos de contrato da instituicao (secretaria). */
export function useContractTemplates() {
  const request = useCallback(() => api.get<ContractTemplate[]>(endpoints.contracts.templates).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: string | null, input: ContractTemplateInput) => {
    if (id) await api.patch(endpoints.contracts.template(id), { name: input.name, body: input.body });
    else await api.post(endpoints.contracts.templates, input);
    reload();
  };
  const setActive = async (id: string, isActive: boolean) => {
    await api.patch(endpoints.contracts.template(id), { is_active: isActive });
    reload();
  };

  return { templates: data, loading, error, save, setActive };
}
