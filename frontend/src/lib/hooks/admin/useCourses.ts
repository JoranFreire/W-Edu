'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Course } from '@/types/course';

/** Catalogo de cursos com criacao, edicao e exclusao. */
export function useCourses() {
  const request = useCallback(() => api.get<Course[]>(endpoints.courses.list).then((response) => response.data), []);
  const { data = [], loading, error, reload } = useApiQuery(request);

  const save = async (courseId: number | null, input: Partial<Course>) => {
    if (courseId) await api.patch(endpoints.courses.detail(courseId), input);
    else await api.post(endpoints.courses.list, input);
    reload();
  };
  const remove = async (courseId: number) => {
    await api.delete(endpoints.courses.detail(courseId));
    reload();
  };

  return { courses: data, loading, error, save, remove };
}
