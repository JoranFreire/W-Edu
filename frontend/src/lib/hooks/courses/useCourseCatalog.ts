'use client';

import { useCallback, useMemo } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Course, Enrollment, LearningPath, LearningPathCourse } from '@/types/course';

interface CatalogData {
  courses: Course[];
  learningPaths: LearningPath[];
  pathCourses: Record<string, LearningPathCourse[]>;
  enrollments: Enrollment[];
}

const EMPTY: CatalogData = { courses: [], learningPaths: [], pathCourses: {}, enrollments: [] };

async function loadPathCourses(path: LearningPath) {
  try {
    const { data } = await api.get<LearningPathCourse[]>(endpoints.learningPaths.courses(path.id));
    return [path.id, [...data].sort((a, b) => a.order - b.order)] as const;
  } catch {
    // Trilha sem cursos acessiveis nao impede o restante do catalogo.
    return [path.id, []] as const;
  }
}

/** Catalogo de cursos e trilhas do aluno, com as matriculas dele e a acao de matricular. */
export function useCourseCatalog(studentId: string | undefined) {
  const request = useCallback(async (): Promise<CatalogData> => {
    if (!studentId) return EMPTY;
    const [courses, learningPaths, enrollments] = await Promise.all([
      api.get<Course[]>(endpoints.courses.list).then((response) => response.data),
      api.get<LearningPath[]>(endpoints.learningPaths.list).then((response) => response.data),
      api.get<Enrollment[]>(endpoints.enrollments.byStudent(studentId)).then((response) => response.data),
    ]);
    const pathCourses = Object.fromEntries(await Promise.all(learningPaths.map(loadPathCourses)));
    return { courses, learningPaths, pathCourses, enrollments };
  }, [studentId]);
  const { data = EMPTY, loading, error, reload } = useApiQuery(request);

  const enrolledIds = useMemo(() => new Set(data.enrollments.map((enrollment) => enrollment.course_id)), [data.enrollments]);
  const isEnrolled = (courseId: string) => enrolledIds.has(courseId);
  const courseName = (courseId: string) => data.courses.find((course) => course.id === courseId)?.name ?? `Curso #${courseId}`;

  const enroll = async (courseId: string) => {
    if (!studentId) return;
    await api.post<Enrollment>(endpoints.enrollments.create, { student_id: studentId, course_id: courseId });
    reload();
  };

  return { ...data, loading, error, isEnrolled, courseName, enroll };
}
