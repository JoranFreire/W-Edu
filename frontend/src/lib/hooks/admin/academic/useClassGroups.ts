'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ClassGroup, Shift } from '@/types/academicGroups';

export interface ClassGroupInput {
  program_id: number;
  term_id: number;
  name: string;
  curriculum_term_number: number | null;
  shift: Shift;
  capacity: number | null;
  homeroom_teacher_id: number | null;
}

function editableFields(input: ClassGroupInput) {
  const { name, curriculum_term_number, shift, capacity, homeroom_teacher_id } = input;
  return { name, curriculum_term_number, shift, capacity, homeroom_teacher_id };
}

/** Turmas-grupo, opcionalmente de um periodo letivo. */
export function useClassGroups(termId?: number) {
  const request = useCallback(
    () => api.get<ClassGroup[]>(endpoints.academic.classGroups, { params: { term_id: termId } }).then((response) => response.data),
    [termId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (id: number | null, input: ClassGroupInput) => {
    // Programa e periodo sao fixos depois de criada a turma.
    if (id) await api.patch(endpoints.academic.classGroup(id), editableFields(input));
    else await api.post(endpoints.academic.classGroups, input);
    reload();
  };
  const remove = async (id: number) => {
    await api.delete(endpoints.academic.classGroup(id));
    reload();
  };

  return { groups: data, loading, error, save, remove };
}
