'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Activity, ActivityInput, FinalProject, Integralization, Internship } from '@/types/completion';

interface MyCompletion {
  integralization: Integralization[];
  activities: Activity[];
  internships: Internship[];
  finalProjects: FinalProject[];
}

/** Visao do aluno: integralizacao, atividades complementares, estagios e TCC; declara e retira atividades. */
export function useMyCompletion() {
  const request = useCallback(async (): Promise<MyCompletion> => {
    const [integralization, activities, internships, finalProjects] = await Promise.all([
      api.get<Integralization[]>(endpoints.completion.myIntegralization),
      api.get<Activity[]>(endpoints.completion.myActivities),
      api.get<Internship[]>(endpoints.completion.myInternships),
      api.get<FinalProject[]>(endpoints.completion.myFinalProjects),
    ]);
    return { integralization: integralization.data, activities: activities.data, internships: internships.data, finalProjects: finalProjects.data };
  }, []);
  const { data, loading, error, reload } = useApiQuery(request);

  const submitActivity = async (enrollmentId: number, input: ActivityInput) => {
    await api.post(endpoints.completion.submitActivity(enrollmentId), input);
    reload();
  };
  const withdrawActivity = async (activityId: number) => {
    await api.delete(endpoints.completion.myActivity(activityId));
    reload();
  };

  return { data, loading, error, reload, submitActivity, withdrawActivity };
}
