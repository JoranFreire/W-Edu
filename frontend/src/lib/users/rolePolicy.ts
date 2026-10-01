import { type User, type UserRole, isAdminIn, roleLabels, rolesOf } from '@/types/auth';

export type RoleOption = [UserRole, string];

const institutionRoles: UserRole[] = ['student', 'instructor', 'coordinator', 'company_manager', 'secretary', 'institution_admin'];
const institutionRoleOptions: RoleOption[] = institutionRoles.map((role) => [role, roleLabels[role]]);
const academicRoleOptions = institutionRoleOptions.filter(([role]) => role === 'student' || role === 'instructor');
const ACADEMIC: UserRole[] = ['student', 'instructor'];

/** Papeis que a pessoa logada pode atribuir (espelha `ensure_can_assign_roles` no backend). */
export function assignableRoles(currentRoles: UserRole[], isSuperAdmin = false): RoleOption[] {
  if (isSuperAdmin) return [...institutionRoleOptions, ['super_admin', roleLabels.super_admin]];
  if (isAdminIn(currentRoles)) return institutionRoleOptions;
  return academicRoleOptions;
}

/** Admins nao sao editados pela tela; coordenacao e gestores so editam quem e apenas aluno e/ou instrutor. */
export function canManageUser(currentRoles: UserRole[], user: User): boolean {
  const target = rolesOf(user);
  if (isAdminIn(target)) return false;
  return isAdminIn(currentRoles) || target.every((role) => ACADEMIC.includes(role));
}
