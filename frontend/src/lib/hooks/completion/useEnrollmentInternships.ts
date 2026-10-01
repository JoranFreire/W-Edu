'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Internship, InternshipInput, InternshipStatus } from '@/types/completion';

/** Estagios da matricula (secretaria): cadastro e mudanca de situacao. */
export function useEnrollmentInternships(enrollmentId: number) {
  const request = useCallback(
    () => api.get<Internship[]>(endpoints.completion.internships(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const create = async (input: InternshipInput) => {
    await api.post(endpoints.completion.internships(enrollmentId), input);
    reload();
  };
  const changeStatus = async (internshipId: number, status: InternshipStatus) => {
    await api.patch(endpoints.completion.internship(internshipId), { status });
    reload();
  };

  return { internships: data, error, create, changeStatus };
}
