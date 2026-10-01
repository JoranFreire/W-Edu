'use client';

import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import type { ClassOffering } from '@/types/schedule';

export interface ClassOfferingInput {
  course_id: string;
  name: string;
  starts_at: string;
  ends_at: string;
  capacity: number;
  status: ClassOffering['status'];
  room_id: string | null;
  instructor_id: string | null;
  term_id: string | null;
  subject_id: string | null;
  class_group_id: string | null;
}

/** Criacao de oferta (turma da agenda), com vinculos academicos opcionais. */
export function useCreateClassOffering() {
  const create = async (input: ClassOfferingInput) => {
    const { data } = await api.post<ClassOffering>(endpoints.schedule.classes, input);
    return data;
  };
  return { create };
}
