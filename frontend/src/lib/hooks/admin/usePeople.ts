'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Organization, User, UserRole } from '@/types/auth';

export interface NewUserInput {
  name: string;
  email: string;
  password: string;
  role: UserRole;
  roles: UserRole[];
  organization_id: string | null;
  birth_date: string | null;
}

export interface UserUpdateInput {
  name: string;
  email: string;
  role: UserRole;
  roles: UserRole[];
  organization_id: string | null;
  is_active: boolean;
  /** Nulo mantem a data atual. */
  birth_date: string | null;
}

export interface OrganizationInput {
  name: string;
  legal_name: string | null;
  document: string | null;
  contact_email: string | null;
  is_active?: boolean;
}

const empty = { users: [] as User[], organizations: [] as Organization[] };

/** Usuarios e empresas da instituicao ativa; toda alteracao recarrega os dados. */
export function usePeople() {
  const request = useCallback(async () => {
    const [users, organizations] = await Promise.all([
      api.get<User[]>('/admin/users'),
      api.get<Organization[]>('/admin/organizations'),
    ]);
    return { users: users.data, organizations: organizations.data };
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
    reload,
    createUser: withReload((input: NewUserInput) => api.post('/admin/users', input)),
    updateUser: withReload((id: string, input: UserUpdateInput) => api.patch(`/admin/users/${id}`, input)),
    deleteUser: withReload((id: string) => api.delete(`/admin/users/${id}`)),
    createOrganization: withReload((input: OrganizationInput) => api.post('/admin/organizations', input)),
    updateOrganization: withReload((id: string, input: OrganizationInput) => api.patch(`/admin/organizations/${id}`, input)),
  };
}
