'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { TeachingOffering } from '@/types/assessment';

export function useTeachingOffering(offeringId: number) {
  const request = useCallback(
    () => api.get<TeachingOffering>(endpoints.assessment.offering(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data, loading, error } = useApiQuery(request);

  const syncGroup = async () => {
    const { data: result } = await api.post<{ created: number }>(endpoints.assessment.syncGroup(offeringId));
    return result.created;
  };

  return { offering: data, loading, error, syncGroup };
}
