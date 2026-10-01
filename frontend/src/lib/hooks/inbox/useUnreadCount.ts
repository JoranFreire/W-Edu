'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InboxSummary } from '@/types/notification';

/** Quantidade de avisos nao lidos do usuario. */
export function useUnreadCount() {
  const request = useCallback(
    () => api.get<InboxSummary>(endpoints.notifications.inboxSummary).then((response) => response.data.unread),
    [],
  );
  const { data = 0 } = useApiQuery(request);
  return data;
}
