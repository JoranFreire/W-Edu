import { type UserRole, hasAnyRole, isAdminIn } from '@/types/auth';

/** Espelha `ensure_can_remove`: remove o registro quem o criou ou a coordenacao. */
export function canRemoveSchoolRecord(userId: string | undefined, roles: UserRole[], authorId: string | null | undefined): boolean {
  if (!userId) return false;
  return isAdminIn(roles) || hasAnyRole(roles, ['coordinator']) || (authorId != null && authorId === userId);
}
