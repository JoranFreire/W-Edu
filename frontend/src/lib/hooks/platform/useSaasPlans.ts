'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { SaasPlan, SaasPlanInput } from '@/types/saas';

/** Catalogo de planos SaaS da plataforma (super admin). */
export function useSaasPlans() {
  const request = useCallback(() => api.get<SaasPlan[]>(endpoints.saas.plans).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: SaasPlanInput) => {
    await api.post(endpoints.saas.plans, input);
    reload();
  };
  const setActive = async (planId: number, isActive: boolean) => {
    await api.patch(endpoints.saas.plan(planId), { is_active: isActive });
    reload();
  };

  return { plans: data, loading, error, create, setActive };
}
