'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AssessmentItem, AssessmentKind } from '@/types/assessment';

export interface AssessmentItemInput {
  name: string;
  kind: AssessmentKind;
  grading_period_id: string | null;
  weight: number;
  max_score: number;
  quiz_id: string | null;
  due_on: string | null;
}

/** Plano de avaliacoes da turma. */
export function useAssessmentItems(offeringId: string) {
  const request = useCallback(
    () => api.get<AssessmentItem[]>(endpoints.assessment.items(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: AssessmentItemInput) => {
    await api.post(endpoints.assessment.items(offeringId), input);
    reload();
  };
  const remove = async (id: string) => {
    await api.delete(endpoints.assessment.item(id));
    reload();
  };

  return { items: data, loading, error, create, remove };
}
