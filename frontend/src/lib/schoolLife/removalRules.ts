import { isAdminRole, type Student } from '@/types/auth';

/** Espelha `ensure_can_remove`: remove o registro quem o criou ou a coordenacao. */
export function canRemoveSchoolRecord(user: Student | null, authorId: string | null | undefined): boolean {
  if (!user) return false;
  return isAdminRole(user.role) || user.role === 'coordinator' || (authorId != null && authorId === user.id);
}
