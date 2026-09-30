'use client';

import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import type { ClassOffering } from '@/types/schedule';

export interface ClassOfferingInput {
  course_id: number;
  name: string;
  starts_at: string;
  ends_at: string;
  capacity: number;
  status: ClassOffering['status'];
  room_id: number | null;
  instructor_id: number | null;
  term_id: number | null;
  subject_id: number | null;
  class_group_id: number | null;
}

/** Criacao de oferta (turma da agenda), com vinculos academicos opcionais. */
export function useCreateClassOffering() {
  const create = async (input: ClassOfferingInput) => {
    const { data } = await api.post<ClassOffering>(endpoints.schedule.classes, input);
    return data;
  };
  return { create };
}
