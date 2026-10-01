'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Activity, ActivityDecisionInput } from '@/types/completion';

/** Atividades complementares da matricula, com a decisao da secretaria. */
export function useEnrollmentActivities(enrollmentId: string) {
  const request = useCallback(
    () => api.get<Activity[]>(endpoints.completion.activities(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const decide = async (activityId: string, input: ActivityDecisionInput) => {
    await api.post(endpoints.completion.activityDecision(activityId), input);
    reload();
  };

  return { activities: data, error, decide };
}
