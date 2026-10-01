'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import { type User, rolesOf } from '@/types/auth';
import type { Course } from '@/types/course';
import type { ClassOffering, Location, Room } from '@/types/schedule';

interface ScheduleSetup {
  courses: Course[];
  locations: Location[];
  rooms: Room[];
  classes: ClassOffering[];
  users: User[];
}

const empty: ScheduleSetup = { courses: [], locations: [], rooms: [], classes: [], users: [] };

/** Cadastros de apoio da agenda: cursos, unidades, salas, turmas e usuarios. */
export function useScheduleSetup() {
  const request = useCallback(async (): Promise<ScheduleSetup> => {
    const [courses, locations, rooms, classes, users] = await Promise.all([
      api.get<Course[]>(endpoints.courses.list),
      api.get<Location[]>(endpoints.schedule.locations),
      api.get<Room[]>(endpoints.schedule.rooms),
      api.get<ClassOffering[]>(endpoints.schedule.classes),
      api.get<User[]>('/admin/users'),
    ]);
    return { courses: courses.data, locations: locations.data, rooms: rooms.data, classes: classes.data, users: users.data };
  }, []);
  const { data = empty, loading, error, reload } = useApiQuery(request);
  const instructors = data.users.filter((user) => rolesOf(user).includes('instructor') && user.is_active);
  return { ...data, instructors, loading, error, reload };
}
