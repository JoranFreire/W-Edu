'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { TimeSlot, TimeSlotInput } from '@/types/registration';

/** Horario semanal de uma oferta. */
export function useOfferingTimeSlots(offeringId: number) {
  const request = useCallback(
    () => api.get<TimeSlot[]>(endpoints.registration.offeringSlots(offeringId)).then((response) => response.data),
    [offeringId],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const add = async (input: TimeSlotInput) => {
    await api.post(endpoints.registration.offeringSlots(offeringId), input);
    reload();
  };
  const remove = async (slotId: number) => {
    await api.delete(endpoints.registration.slot(slotId));
    reload();
  };

  return { slots: data, error, add, remove };
}
