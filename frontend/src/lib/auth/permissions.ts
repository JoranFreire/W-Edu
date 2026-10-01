import { isAdminRole, type UserRole } from '@/types/auth';

const coordinatorAdminPaths = [
  '/admin/academic',
  '/admin/secretariat',
  '/admin/courses',
  '/admin/learning-paths',
  '/admin/schedule',
  '/admin/certificates',
  '/admin/notifications',
  '/admin/users',
  '/admin/students',
];

const companyManagerAdminPaths = [
  '/admin/finance',
  '/admin/documents',
  '/admin/analytics',
  '/admin/users',
  '/admin/students',
];

function matchesPath(pathname: string, allowedPath: string) {
  return pathname === allowedPath || pathname.startsWith(`${allowedPath}/`);
}

/** Areas liberadas por permissao (RBAC), alem das liberadas pelo papel. */
const permissionPaths: [string, string[]][] = [
  ['/admin/secretariat', ['secretariat.access']],
  ['/teaching', ['teaching.access']],
  ['/admin/academic', ['academic.manage']],
  ['/admin/courses', ['academic.manage']],
  ['/admin/learning-paths', ['academic.manage']],
  ['/admin/schedule', ['academic.manage']],
  ['/admin/certificates', ['academic.manage']],
  ['/admin/notifications', ['academic.manage']],
  ['/admin/access', ['access.manage']],
  ['/admin/warehouse', ['warehouse.manage', 'warehouse.reports']],
];

function grantedByPermission(pathname: string, permissions: string[]) {
  return permissionPaths.some(([path, required]) => matchesPath(pathname, path) && required.some((key) => permissions.includes(key)));
}

export function canAccessPath(role: UserRole | undefined, pathname: string, permissions: string[] = []) {
  if (!role) return false;
  if (grantedByPermission(pathname, permissions)) return true;
  if (matchesPath(pathname, '/platform')) return role === 'super_admin';
  if (matchesPath(pathname, '/guardian')) return role === 'guardian';
  if (matchesPath(pathname, '/teaching')) return isAdminRole(role) || role === 'coordinator' || role === 'instructor';
  if (!pathname.startsWith('/admin')) return true;
  if (isAdminRole(role)) return true;
  if (role === 'coordinator') return coordinatorAdminPaths.some((path) => matchesPath(pathname, path));
  if (role === 'company_manager') return companyManagerAdminPaths.some((path) => matchesPath(pathname, path));
  if (role === 'secretary') return matchesPath(pathname, '/admin/secretariat');
  return false;
}
