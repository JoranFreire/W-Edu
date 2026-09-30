'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ProgramEnrollment, ProgramEnrollmentStatus } from '@/types/academicGroups';

export interface ProgramEnrollmentInput {
  student_id: number;
  program_id: number;
  entry_term_id: number | null;
  registration_number: string | null;
}

export interface ProgramEnrollmentFilters {
  program_id?: number;
  status?: ProgramEnrollmentStatus;
}

/** Matriculas no programa (com filtros), criacao e mudanca de situacao. */
export function useProgramEnrollments(filters: ProgramEnrollmentFilters) {
  const { program_id: programId, status } = filters;
  const request = useCallback(
    () => api.get<ProgramEnrollment[]>(endpoints.academic.programEnrollments, { params: { program_id: programId, status } })
      .then((response) => response.data),
    [programId, status],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const create = async (input: ProgramEnrollmentInput) => {
    const { data: created } = await api.post<ProgramEnrollment>(endpoints.academic.programEnrollments, input);
    reload();
    return created;
  };
  const changeStatus = async (id: number, next: ProgramEnrollmentStatus) => {
    await api.post(endpoints.academic.programEnrollmentStatus(id), { status: next });
    reload();
  };

  return { enrollments: data, loading, error, create, changeStatus };
}
