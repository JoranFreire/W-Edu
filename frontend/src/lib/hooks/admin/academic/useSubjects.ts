'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Subject } from '@/types/academic';

export interface SubjectInput {
  code: string;
  name: string;
  syllabus: string | null;
  hours: number;
  credits: number | null;
  course_id: string | null;
  is_active: boolean;
}

/** Disciplinas da instituicao ativa; toda alteracao recarrega a lista. */
export function useSubjects() {
  const request = useCallback(() => api.get<Subject[]>(endpoints.academic.subjects).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: string | null, input: SubjectInput) => {
    if (id) await api.patch(endpoints.academic.subject(id), input);
    else await api.post(endpoints.academic.subjects, input);
    reload();
  };
  const remove = async (subject: Subject) => {
    await api.delete(endpoints.academic.subject(subject.id));
    reload();
  };

  return { subjects: data, loading, error, save, remove };
}
