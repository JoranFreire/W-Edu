import { type RoleFilter, isRoleFilter, matchesRoleFilter, matchesSearch, roleFilters } from '@/lib/users/roleFilters';
import type { User } from '@/types/auth';

export type StatusFilter = 'all' | 'active' | 'inactive';
export type UserSort = 'name' | 'recent' | 'oldest';
/** `all`, `none` (sem empresa) ou o id da empresa. */
export type OrganizationFilter = string;

export interface UserFilters {
  role: RoleFilter;
  status: StatusFilter;
  organization: OrganizationFilter;
  sort: UserSort;
}

export const DEFAULT_FILTERS: UserFilters = { role: 'all', status: 'all', organization: 'all', sort: 'name' };

export const statusOptions: { id: StatusFilter; label: string }[] = [
  { id: 'all', label: 'Todas as situações' },
  { id: 'active', label: 'Ativos' },
  { id: 'inactive', label: 'Inativos' },
];

export const sortOptions: { id: UserSort; label: string }[] = [
  { id: 'name', label: 'Nome (A–Z)' },
  { id: 'recent', label: 'Cadastro mais recente' },
  { id: 'oldest', label: 'Cadastro mais antigo' },
];

/** Filtros salvos no navegador; valores desconhecidos voltam ao padrao. */
export function parseFilters(stored: string | null): UserFilters {
  try {
    const raw = stored ? (JSON.parse(stored) as Partial<UserFilters>) : {};
    return {
      role: isRoleFilter(raw.role ?? null) ? (raw.role as RoleFilter) : DEFAULT_FILTERS.role,
      status: statusOptions.some((option) => option.id === raw.status) ? (raw.status as StatusFilter) : DEFAULT_FILTERS.status,
      organization: typeof raw.organization === 'string' ? raw.organization : DEFAULT_FILTERS.organization,
      sort: sortOptions.some((option) => option.id === raw.sort) ? (raw.sort as UserSort) : DEFAULT_FILTERS.sort,
    };
  } catch {
    return DEFAULT_FILTERS;
  }
}

function matchesStatus(user: User, status: StatusFilter): boolean {
  return status === 'all' || (status === 'active') === user.is_active;
}

function matchesOrganization(user: User, organization: OrganizationFilter): boolean {
  if (organization === 'all') return true;
  if (organization === 'none') return !user.organization_id;
  return user.organization_id === organization;
}

const collator = new Intl.Collator('pt-BR', { sensitivity: 'base' });

function compare(sort: UserSort) {
  if (sort === 'recent') return (a: User, b: User) => b.created_at.localeCompare(a.created_at);
  if (sort === 'oldest') return (a: User, b: User) => a.created_at.localeCompare(b.created_at);
  return (a: User, b: User) => collator.compare(a.name, b.name);
}

/** Aplica perfil, situacao, empresa e busca, na ordem escolhida. */
export function applyFilters(users: User[], filters: UserFilters, query: string): User[] {
  return users
    .filter((user) => matchesRoleFilter(user, filters.role) && matchesStatus(user, filters.status)
      && matchesOrganization(user, filters.organization) && matchesSearch(user, query))
    .sort(compare(filters.sort));
}

/** Quantos usuarios cada perfil teria com os demais filtros e a busca atuais. */
export function countByRole(users: User[], filters: UserFilters, query: string): Record<RoleFilter, number> {
  const base = users.filter((user) => matchesStatus(user, filters.status) && matchesOrganization(user, filters.organization) && matchesSearch(user, query));
  return Object.fromEntries(roleFilters.map(({ id }) => [id, base.filter((user) => matchesRoleFilter(user, id)).length])) as Record<RoleFilter, number>;
}

/** Filtros diferentes do padrao (a ordenacao nao conta como filtro). */
export function activeFilterCount(filters: UserFilters, query: string): number {
  return [filters.role !== 'all', filters.status !== 'all', filters.organization !== 'all', query.trim() !== ''].filter(Boolean).length;
}
