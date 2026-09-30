import { type User, type UserRole, isAdminRole, roleLabels } from '@/types/auth';

type RoleOption = [UserRole, string];

const institutionRoles: UserRole[] = ['student', 'instructor', 'coordinator', 'company_manager', 'secretary', 'institution_admin'];
const institutionRoleOptions: RoleOption[] = institutionRoles.map((role) => [role, roleLabels[role]]);
const academicRoleOptions = institutionRoleOptions.filter(([role]) => role === 'student' || role === 'instructor');

/** Papeis que o usuario atual pode atribuir (espelha as regras do backend). */
export function assignableRoles(currentRole: UserRole | undefined): RoleOption[] {
  if (currentRole === 'super_admin') return [...institutionRoleOptions, ['super_admin', roleLabels.super_admin]];
  if (isAdminRole(currentRole)) return institutionRoleOptions;
  return academicRoleOptions;
}

/** Admins nao sao editados pela tela; coordenacao e gestores so editam alunos e instrutores. */
export function canManageUser(currentRole: UserRole | undefined, user: User): boolean {
  if (isAdminRole(user.role)) return false;
  return isAdminRole(currentRole) || user.role === 'student' || user.role === 'instructor';
}
