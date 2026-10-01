'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ClassOffering } from '@/types/schedule';

/** Turmas da instituicao para escolher no edital. */
export function useClassOfferingOptions() {
  const request = useCallback(() => api.get<ClassOffering[]>(endpoints.schedule.classes).then((response) => response.data), []);
  return useApiQuery(request).data ?? [];
}
