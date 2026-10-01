'use client';

import { useMemo, useState } from 'react';
import { useStoredValue } from '@/lib/hooks/useStoredValue';
import { type RoleFilter, isRoleFilter, matchesRoleFilter, matchesSearch, roleFilters } from '@/lib/users/roleFilters';
import type { User } from '@/types/auth';

/** Filtro por perfil (lembrado no navegador, para voltar do dossie no mesmo filtro) e busca por nome/e-mail. */
export function useUserFilters(users: User[]) {
  const [stored, setStored] = useStoredValue('w-edu-users-role-filter');
  const filter: RoleFilter = isRoleFilter(stored) ? stored : 'all';
  const [query, setQuery] = useState('');

  const counts = useMemo(
    () => Object.fromEntries(roleFilters.map(({ id }) => [id, users.filter((user) => matchesRoleFilter(user, id)).length])) as Record<RoleFilter, number>,
    [users],
  );
  const filtered = useMemo(
    () => users.filter((user) => matchesRoleFilter(user, filter) && matchesSearch(user, query)),
    [users, filter, query],
  );

  return { filter, setFilter: (next: RoleFilter) => setStored(next), query, setQuery, counts, filtered };
}
