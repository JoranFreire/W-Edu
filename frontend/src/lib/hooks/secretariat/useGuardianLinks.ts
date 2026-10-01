'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { GuardianLink, GuardianRelationship } from '@/types/guardians';

export interface GuardianLinkInput {
  name: string;
  email: string;
  password: string | null;
  relationship_kind: GuardianRelationship;
  is_financial: boolean;
  can_pick_up: boolean;
  is_primary: boolean;
}

export type GuardianFlags = Partial<Pick<GuardianLink, 'is_financial' | 'can_pick_up' | 'is_primary'>>;

/** Responsaveis vinculados ao aluno (secretaria). */
export function useGuardianLinks(studentId: string) {
  const request = useCallback(
    () => api.get<GuardianLink[]>(endpoints.guardians.links(studentId)).then((response) => response.data),
    [studentId],
  );
  const { data = [], error, reload } = useApiQuery(request);

  const add = async (input: GuardianLinkInput) => {
    await api.post(endpoints.guardians.links(studentId), input);
    reload();
  };
  const update = async (linkId: string, flags: GuardianFlags) => {
    await api.patch(endpoints.guardians.link(linkId), flags);
    reload();
  };
  const remove = async (linkId: string) => {
    await api.delete(endpoints.guardians.link(linkId));
    reload();
  };

  return { links: data, error, add, update, remove };
}
