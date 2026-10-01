'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ClassGroup, ClassGroupMember } from '@/types/academicGroups';

interface ClassGroupData {
  group: ClassGroup;
  members: ClassGroupMember[];
}

/** Uma turma-grupo e seus alunos, com alocacao e remocao. */
export function useClassGroup(groupId: string) {
  const request = useCallback(async (): Promise<ClassGroupData> => {
    const [group, members] = await Promise.all([
      api.get<ClassGroup>(endpoints.academic.classGroup(groupId)),
      api.get<ClassGroupMember[]>(endpoints.academic.classGroupMembers(groupId)),
    ]);
    return { group: group.data, members: members.data };
  }, [groupId]);
  const { data, loading, error, reload } = useApiQuery(request);

  const addMember = async (enrollmentId: string) => {
    await api.post(endpoints.academic.classGroupMembers(groupId), { program_enrollment_id: enrollmentId });
    reload();
  };
  const removeMember = async (enrollmentId: string) => {
    await api.delete(endpoints.academic.classGroupMember(groupId, enrollmentId));
    reload();
  };

  return { group: data?.group, members: data?.members ?? [], loading, error, addMember, removeMember };
}
