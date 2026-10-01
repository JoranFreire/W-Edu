'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ScheduledMeeting } from '@/types/schedule';
import type { BenefitItem, Delivery } from '@/types/socialPrograms';

interface OfferingBenefits {
  meetings: ScheduledMeeting[];
  items: BenefitItem[];
  deliveries: Delivery[];
}

/** Encontros, itens e entregas da turma; entrega em lote por encontro. */
export function useOfferingBenefits(offeringId: string) {
  const request = useCallback(async (): Promise<OfferingBenefits> => {
    const [meetings, items, deliveries] = await Promise.all([
      api.get<ScheduledMeeting[]>(endpoints.schedule.classMeetings(offeringId)),
      api.get<BenefitItem[]>(endpoints.social.items),
      api.get<Delivery[]>(endpoints.social.offeringDeliveries(offeringId)),
    ]);
    return { meetings: meetings.data, items: items.data.filter((item) => item.is_active), deliveries: deliveries.data };
  }, [offeringId]);
  const { data, error, reload } = useApiQuery(request);
  const deliver = async (meetingId: string, itemId: string, quantity: number) => {
    const { data: result } = await api.post<{ delivered: number; remaining_stock: number }>(
      endpoints.social.meetingDeliveries(meetingId), { item_id: itemId, quantity },
    );
    reload();
    return result;
  };
  return { benefits: data, error, deliver, reload };
}
