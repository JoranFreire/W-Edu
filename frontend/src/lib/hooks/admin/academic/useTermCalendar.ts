'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { CalendarEvent, CalendarEventKind, TermCalendarSummary } from '@/types/academicCalendar';

export interface CalendarEventInput {
  kind: CalendarEventKind;
  title: string;
  starts_on: string;
  ends_on: string | null;
}

interface TermCalendarData {
  events: CalendarEvent[];
  summary: TermCalendarSummary;
}

/** Eventos do calendario de um periodo letivo e a contagem de dias letivos. */
export function useTermCalendar(termId: string) {
  const request = useCallback(async (): Promise<TermCalendarData> => {
    const [events, summary] = await Promise.all([
      api.get<CalendarEvent[]>(endpoints.academic.calendarEvents, { params: { term_id: termId } }),
      api.get<TermCalendarSummary>(endpoints.academic.termCalendarSummary(termId)),
    ]);
    return { events: events.data, summary: summary.data };
  }, [termId]);
  const { data, loading, error, reload } = useApiQuery(request);

  const add = async (input: CalendarEventInput) => {
    await api.post(endpoints.academic.calendarEvents, { ...input, term_id: termId });
    reload();
  };
  const remove = async (id: string) => {
    await api.delete(endpoints.academic.calendarEvent(id));
    reload();
  };

  return { events: data?.events ?? [], summary: data?.summary, loading, error, add, remove };
}
