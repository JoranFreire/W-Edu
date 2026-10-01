'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Course, Enrollment, Progress, Session } from '@/types/course';

interface DashboardData {
  enrollments: Enrollment[];
  progress: Progress[];
  sessions: Session[];
  courses: Course[];
}

/** Resumo do aluno: matriculas, progresso, sessoes de voz e cursos matriculados. */
export function useStudentDashboard(studentId: number | undefined) {
  const request = useCallback(async (): Promise<DashboardData | undefined> => {
    if (!studentId) return undefined;
    const [enrollments, progress, sessions, courses] = await Promise.all([
      api.get<Enrollment[]>(endpoints.enrollments.byStudent(studentId)),
      api.get<Progress[]>(endpoints.progress.me),
      api.get<Session[]>(endpoints.sessions.me),
      api.get<Course[]>(endpoints.courses.list),
    ]);
    return { enrollments: enrollments.data, progress: progress.data, sessions: sessions.data, courses: courses.data };
  }, [studentId]);
  const { data, loading } = useApiQuery(request);
  const enrolledCourses = data ? data.courses.filter((course) => data.enrollments.some((e) => e.course_id === course.id)) : [];
  return { data, enrolledCourses, loading: loading || !data };
}
