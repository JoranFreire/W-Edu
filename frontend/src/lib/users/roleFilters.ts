import { type User, type UserRole, rolesOf } from '@/types/auth';

export type RoleFilter = 'all' | 'students' | 'guardians' | 'instructors' | 'coordinators' | 'secretaries' | 'admins' | 'managers';

/** Filtros pre-definidos da lista de usuarios: cada um reune os papeis equivalentes. */
export const roleFilters: { id: RoleFilter; label: string; roles: UserRole[] | null }[] = [
  { id: 'all', label: 'Todos', roles: null },
  { id: 'students', label: 'Alunos', roles: ['student'] },
  { id: 'guardians', label: 'Responsáveis', roles: ['guardian'] },
  { id: 'instructors', label: 'Professores', roles: ['instructor'] },
  { id: 'coordinators', label: 'Coordenação', roles: ['coordinator'] },
  { id: 'secretaries', label: 'Secretaria', roles: ['secretary'] },
  { id: 'admins', label: 'Administradores', roles: ['admin', 'institution_admin', 'super_admin'] },
  { id: 'managers', label: 'Gestores de empresa', roles: ['company_manager'] },
];

export function isRoleFilter(value: string | null): value is RoleFilter {
  return roleFilters.some((filter) => filter.id === value);
}

export function matchesRoleFilter(user: User, filter: RoleFilter): boolean {
  const roles = roleFilters.find((item) => item.id === filter)?.roles;
  return !roles || rolesOf(user).some((role) => roles.includes(role));
}

/** Busca sem acento e sem diferenciar maiusculas, por nome ou e-mail. */
export function matchesSearch(user: User, query: string): boolean {
  const normalize = (text: string) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const term = normalize(query.trim());
  return !term || normalize(user.name).includes(term) || normalize(user.email).includes(term);
}
