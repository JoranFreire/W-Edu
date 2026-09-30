'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Student } from '@/types/auth';
import type { Course } from '@/types/course';

const empty = { courses: [] as Course[], students: [] as Student[] };

/** Cursos e usuarios usados na gestao de certificados. */
export function useCertificateCatalog() {
  const request = useCallback(async () => {
    const [courses, students] = await Promise.all([
      api.get<Course[]>(endpoints.courses.list),
      api.get<Student[]>('/admin/users'),
    ]);
    return { courses: courses.data, students: students.data };
  }, []);
  const { data = empty, loading, error } = useApiQuery(request);
  return { ...data, loading, error };
}
