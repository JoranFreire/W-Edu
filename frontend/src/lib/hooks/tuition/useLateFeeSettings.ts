'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { LateFeeSettings } from '@/types/tuition';

/** Multa e juros de mora da instituicao. */
export function useLateFeeSettings() {
  const request = useCallback(() => api.get<LateFeeSettings>(endpoints.tuition.settings).then((response) => response.data), []);
  const { data, error, reload } = useApiQuery(request);
  const save = async (input: LateFeeSettings) => {
    await api.put(endpoints.tuition.settings, input);
    reload();
  };
  return { settings: data, error, save };
}
