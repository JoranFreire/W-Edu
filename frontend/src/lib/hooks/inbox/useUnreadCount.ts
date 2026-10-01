'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InboxSummary } from '@/types/notification';

/** Avisos nao lidos; `refreshKey` (ex.: a rota atual) refaz a contagem ao navegar. */
export function useUnreadCount(refreshKey: string) {
  const request = useCallback(
    () => api.get<InboxSummary>(endpoints.notifications.inboxSummary, { params: { _: refreshKey } }).then((response) => response.data.unread),
    [refreshKey],
  );
  const { data = 0 } = useApiQuery(request);
  return data;
}
