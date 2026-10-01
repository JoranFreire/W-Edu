'use client';

import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import type { OccurrenceInput } from '@/types/schoolLife';

/** Registro de ocorrencia sem listagem (professor na turma). */
export function useOccurrenceRegistration() {
  const register = async (input: OccurrenceInput) => {
    await api.post(endpoints.school.occurrences, input);
  };
  return { register };
}
