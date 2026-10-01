'use client';

import { useMemo, useState } from 'react';
import { useStoredValue } from '@/lib/hooks/useStoredValue';
import { DEFAULT_FILTERS, type UserFilters, activeFilterCount, applyFilters, countByRole, parseFilters } from '@/lib/users/userFilters';
import type { User } from '@/types/auth';

/** Filtros da lista de usuarios: lembrados no navegador (para voltar do dossie igual); a busca vale so na tela. */
export function useUserFilters(users: User[]) {
  const [stored, setStored] = useStoredValue('w-edu-users-filters');
  const filters = useMemo(() => parseFilters(stored), [stored]);
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => applyFilters(users, filters, query), [users, filters, query]);
  const counts = useMemo(() => countByRole(users, filters, query), [users, filters, query]);

  const update = (patch: Partial<UserFilters>) => setStored(JSON.stringify({ ...filters, ...patch }));
  const reset = () => {
    setStored(JSON.stringify({ ...DEFAULT_FILTERS, sort: filters.sort }));
    setQuery('');
  };

  return { filters, update, reset, query, setQuery, filtered, counts, active: activeFilterCount(filters, query) };
}
