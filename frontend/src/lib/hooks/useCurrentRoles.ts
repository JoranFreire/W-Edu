'use client';

import { useAuthStore } from '@/store/authStore';
import { type UserRole, hasAnyRole, isAdminIn, rolesOf } from '@/types/auth';

/** Papeis da pessoa logada na instituicao ativa (pode acumular varios: aluno e professor, por exemplo). */
export function useCurrentRoles() {
  const student = useAuthStore((state) => state.student);
  const stored = useAuthStore((state) => state.roles);
  const roles: UserRole[] = stored.length ? stored : rolesOf(student);
  return {
    roles,
    has: (...wanted: UserRole[]) => hasAnyRole(roles, wanted),
    isAdmin: isAdminIn(roles),
    isSuperAdmin: student?.role === 'super_admin',
  };
}
