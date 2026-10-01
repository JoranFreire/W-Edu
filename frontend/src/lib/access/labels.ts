import type { UserRole } from '@/types/auth';
import type { PermissionDef } from '@/types/access';

export const roleLabels: Partial<Record<UserRole, string>> = {
  institution_admin: 'Administrador da instituição',
  coordinator: 'Coordenação',
  instructor: 'Instrutor/professor',
  secretary: 'Secretaria',
  company_manager: 'Gestor de empresa',
  student: 'Aluno',
};

/** Permissoes agrupadas pelo modulo do catalogo, na ordem em que aparecem. */
export function groupByModule(catalog: PermissionDef[]): [string, PermissionDef[]][] {
  const groups = new Map<string, PermissionDef[]>();
  for (const permission of catalog) groups.set(permission.module, [...(groups.get(permission.module) ?? []), permission]);
  return [...groups.entries()];
}
