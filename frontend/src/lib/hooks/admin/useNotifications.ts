'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { NotificationEvent, NotificationTemplate } from '@/types/notification';

interface NotificationsData {
  templates: NotificationTemplate[];
  events: NotificationEvent[];
  eventsUnavailable: boolean;
}

const empty: NotificationsData = { templates: [], events: [], eventsUnavailable: false };

/** Templates e fila de eventos de comunicacao; a fila pode falhar sem derrubar os templates. */
export function useNotifications() {
  const request = useCallback(async (): Promise<NotificationsData> => {
    const [templates, events] = await Promise.allSettled([
      api.get<NotificationTemplate[]>(endpoints.notifications.templates),
      api.get<NotificationEvent[]>(endpoints.notifications.events),
    ]);
    return {
      templates: templates.status === 'fulfilled' ? templates.value.data : [],
      events: events.status === 'fulfilled' ? events.value.data : [],
      eventsUnavailable: events.status === 'rejected',
    };
  }, []);
  const { data = empty, loading, error, reload } = useApiQuery(request);

  const processDue = async () => {
    const { data: processed } = await api.post<NotificationEvent[]>(endpoints.notifications.processDue);
    reload();
    return processed.length;
  };
  const markSent = async (id: number) => {
    await api.post(endpoints.notifications.eventSent(id));
    reload();
  };
  const markFailed = async (id: number, reason: string) => {
    await api.post(endpoints.notifications.eventFailed(id), null, { params: { error_message: reason } });
    reload();
  };

  return { ...data, loading, error, reload, processDue, markSent, markFailed };
}
