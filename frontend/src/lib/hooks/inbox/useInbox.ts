'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { InboxNotice } from '@/types/notification';

/** Caixa de avisos do usuario autenticado, com marcacao de leitura. */
export function useInbox(unreadOnly: boolean) {
  const request = useCallback(
    () => api.get<InboxNotice[]>(endpoints.notifications.inbox, { params: { unread_only: unreadOnly } }).then((response) => response.data),
    [unreadOnly],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const markRead = async (noticeId: number) => {
    await api.post(endpoints.notifications.inboxRead(noticeId));
    reload();
  };
  const markAllRead = async () => {
    await api.post(endpoints.notifications.inboxReadAll);
    reload();
  };

  return { notices: data, loading, error, markRead, markAllRead };
}
