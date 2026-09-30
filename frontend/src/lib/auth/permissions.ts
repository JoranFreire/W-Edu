import { isAdminRole, type UserRole } from '@/types/auth';

const coordinatorAdminPaths = [
  '/admin/academic',
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

export function canAccessPath(role: UserRole | undefined, pathname: string) {
  if (!role) return false;
  if (matchesPath(pathname, '/platform')) return role === 'super_admin';
  if (!pathname.startsWith('/admin')) return true;
  if (isAdminRole(role)) return true;
  if (role === 'coordinator') return coordinatorAdminPaths.some((path) => matchesPath(pathname, path));
  if (role === 'company_manager') return companyManagerAdminPaths.some((path) => matchesPath(pathname, path));
  return false;
}
