'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { NotificationEvent, NotificationTemplate, NotificationTemplateInput } from '@/types/notification';

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
  const retryEvent = async (id: string) => {
    await api.post(endpoints.notifications.eventRetry(id));
    reload();
  };
  /** Cria o template ou, quando ja existe (`isNew` falso), altera titulo, mensagem e situacao. */
  const saveTemplate = async (input: NotificationTemplateInput, isNew: boolean) => {
    const { key, channel, title_template, body_template, is_active } = input;
    if (isNew) await api.post(endpoints.notifications.templates, { key, channel, title_template, body_template });
    else await api.patch(endpoints.notifications.template(key, channel), { title_template, body_template, is_active });
    reload();
  };

  return { ...data, loading, error, reload, processDue, retryEvent, saveTemplate };
}
