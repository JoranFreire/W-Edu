'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AccessMember, AccessRole, AccessRoleInput, BuiltInProfile, PermissionDef } from '@/types/access';

interface AccessAdminData {
  catalog: PermissionDef[];
  builtIn: BuiltInProfile[];
  roles: AccessRole[];
  members: AccessMember[];
}

/** Perfis de acesso: catalogo, perfis padrao, perfis personalizados e membros elegiveis. */
export function useAccessAdmin() {
  const request = useCallback(async (): Promise<AccessAdminData> => {
    const [catalog, builtIn, roles, members] = await Promise.all([
      api.get<PermissionDef[]>(endpoints.access.permissions),
      api.get<BuiltInProfile[]>(endpoints.access.builtIn),
      api.get<AccessRole[]>(endpoints.access.roles),
      api.get<AccessMember[]>(endpoints.access.members),
    ]);
    return { catalog: catalog.data, builtIn: builtIn.data, roles: roles.data, members: members.data };
  }, []);
  const { data, error, reload } = useApiQuery(request);

  const run = async (action: () => Promise<unknown>) => {
    await action();
    reload();
  };

  return {
    data,
    error,
    save: (id: string | null, input: AccessRoleInput) =>
      run(() => (id ? api.put(endpoints.access.role(id), input) : api.post(endpoints.access.roles, input))),
    remove: (id: string) => run(() => api.delete(endpoints.access.role(id))),
    assign: (id: string, userId: string) => run(() => api.post(endpoints.access.roleMembers(id), { user_id: userId })),
    unassign: (id: string, userId: string) => run(() => api.delete(endpoints.access.roleMember(id, userId))),
  };
}
