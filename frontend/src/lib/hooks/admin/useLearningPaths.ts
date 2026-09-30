'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Course, LearningPath, LearningPathCourse } from '@/types/course';

interface LearningPathsData {
  paths: LearningPath[];
  courses: Course[];
  pathCourses: Record<number, LearningPathCourse[]>;
}

export interface LearningPathInput {
  name: string;
  description: string | null;
}

const empty: LearningPathsData = { paths: [], courses: [], pathCourses: {} };

/** Trilhas, seus cursos e as operacoes de cadastro; toda alteracao recarrega os dados. */
export function useLearningPaths() {
  const request = useCallback(async (): Promise<LearningPathsData> => {
    const [paths, courses] = await Promise.all([
      api.get<LearningPath[]>(endpoints.learningPaths.list),
      api.get<Course[]>(endpoints.courses.list),
    ]);
    const links = await Promise.all(
      paths.data.map((path) => api.get<LearningPathCourse[]>(endpoints.learningPaths.courses(path.id)).then((r) => [path.id, r.data] as const)),
    );
    return { paths: paths.data, courses: courses.data, pathCourses: Object.fromEntries(links) };
  }, []);
  const { data = empty, loading, error, reload } = useApiQuery(request);

  const withReload = <A extends unknown[]>(action: (...args: A) => Promise<unknown>) => async (...args: A) => {
    await action(...args);
    reload();
  };

  return {
    ...data,
    loading,
    error,
    savePath: withReload((pathId: number | null, input: LearningPathInput) =>
      pathId ? api.patch(endpoints.learningPaths.detail(pathId), input) : api.post(endpoints.learningPaths.list, input)),
    deletePath: withReload((pathId: number) => api.delete(endpoints.learningPaths.detail(pathId))),
    addCourse: withReload((pathId: number, courseId: number) =>
      api.post(endpoints.learningPaths.courses(pathId), { course_id: courseId, order: (data.pathCourses[pathId]?.length ?? 0) + 1 })),
    removeCourse: withReload((pathId: number, courseId: number) =>
      api.delete(`${endpoints.learningPaths.courses(pathId)}/${courseId}`)),
  };
}
