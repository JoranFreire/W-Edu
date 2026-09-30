'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ProgramEnrollment } from '@/types/academicGroups';
import type { EnrollmentEvent, TermRegistration } from '@/types/secretariat';

interface EnrollmentFile {
  enrollment: ProgramEnrollment;
  events: EnrollmentEvent[];
  registrations: TermRegistration[];
}

export type MovementAction = 'lock' | 'reactivate' | 'cancel' | 'drop';

/** Ficha da matricula (dados, linha do tempo e rematriculas) e suas movimentacoes. */
export function useEnrollmentFile(enrollmentId: number) {
  const request = useCallback(async (): Promise<EnrollmentFile> => {
    const [enrollment, events, registrations] = await Promise.all([
      api.get<ProgramEnrollment>(endpoints.secretariat.enrollment(enrollmentId)),
      api.get<EnrollmentEvent[]>(endpoints.secretariat.events(enrollmentId)),
      api.get<TermRegistration[]>(endpoints.secretariat.registrations(enrollmentId)),
    ]);
    return { enrollment: enrollment.data, events: events.data, registrations: registrations.data };
  }, [enrollmentId]);
  const { data, loading, error, reload } = useApiQuery(request);

  const run = async <T>(action: () => Promise<T>) => {
    const result = await action();
    reload();
    return result;
  };

  return {
    file: data,
    loading,
    error,
    move: (action: MovementAction, reason: string | null) =>
      run(() => api.post(endpoints.secretariat.action(enrollmentId, action), { reason })),
    reenroll: (termId: number, termNumber: number | null) =>
      run(() => api.post(endpoints.secretariat.registrations(enrollmentId), { term_id: termId, curriculum_term_number: termNumber })),
    transferOut: (destination: string, reason: string | null) =>
      run(() => api.post(endpoints.secretariat.action(enrollmentId, 'transfer-out'), { destination, reason })),
    transferInternal: (programId: number, reason: string | null) =>
      run(() => api.post<ProgramEnrollment>(endpoints.secretariat.action(enrollmentId, 'transfer-internal'), { program_id: programId, reason })
        .then((response) => response.data)),
    changeCurriculum: (curriculumId: number, reason: string | null) =>
      run(() => api.post(endpoints.secretariat.action(enrollmentId, 'change-curriculum'), { curriculum_id: curriculumId, reason })),
  };
}
