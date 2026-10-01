'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { GenerationResult, TuitionPlan, TuitionPlanInput } from '@/types/tuition';

/** Planos de mensalidade: cadastro, ativacao e geracao das parcelas. */
export function useTuitionPlans() {
  const request = useCallback(() => api.get<TuitionPlan[]>(endpoints.tuition.plans).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: TuitionPlanInput) => {
    await api.post(endpoints.tuition.plans, input);
    reload();
  };
  const setActive = async (planId: string, isActive: boolean) => {
    await api.patch(endpoints.tuition.plan(planId), { is_active: isActive });
    reload();
  };
  const generate = async (planId: string) => (await api.post<GenerationResult>(endpoints.tuition.generate(planId))).data;

  return { plans: data, loading, error, create, setActive, generate };
}
