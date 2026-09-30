'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { CourseModule, CoursePrerequisite, Lesson } from '@/types/course';

/** Modulos, aulas e pre-requisitos de um curso, cada um recarregavel separadamente. */
export function useCourseContent(courseId: number) {
  const modules = useApiQuery(useCallback(
    () => api.get<CourseModule[]>(endpoints.courses.modules(courseId)).then((response) => response.data), [courseId]));
  const lessons = useApiQuery(useCallback(
    () => api.get<Lesson[]>(endpoints.courses.lessons(courseId)).then((response) => response.data), [courseId]));
  const prerequisites = useApiQuery(useCallback(
    () => api.get<CoursePrerequisite[]>(endpoints.courses.prerequisites(courseId)).then((response) => response.data), [courseId]));

  return {
    modules: modules.data ?? [],
    lessons: lessons.data ?? [],
    prerequisites: prerequisites.data ?? [],
    loading: modules.loading || lessons.loading || prerequisites.loading,
    error: modules.error || lessons.error || prerequisites.error,
    // Alterar modulos pode mudar o agrupamento das aulas.
    reloadModules: () => { modules.reload(); lessons.reload(); },
    reloadLessons: lessons.reload,
    reloadPrerequisites: prerequisites.reload,
  };
}
