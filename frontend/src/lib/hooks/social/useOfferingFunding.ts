'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ClassOffering } from '@/types/schedule';

/** Turmas com financiador e limite de faltas (coordenacao altera). */
export function useOfferingFunding() {
  const request = useCallback(() => api.get<ClassOffering[]>(endpoints.schedule.classes).then((response) => response.data), []);
  const { data = [], reload } = useApiQuery(request);
  const save = async (offeringId: number, fundingSourceId: number | null, maxAbsencePercent: number | null) => {
    await api.patch(endpoints.schedule.class(offeringId), { funding_source_id: fundingSourceId, max_absence_percent: maxAbsencePercent });
    reload();
  };
  return { offerings: data, save };
}
