import { type UserRole, isAdminRole, roleLabels } from '@/types/auth';

function badgeCls(role: UserRole) {
  if (isAdminRole(role)) return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400';
  if (role === 'instructor' || role === 'coordinator') return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400';
  if (role === 'guardian') return 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300';
  return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
}

/** Um selo por papel da pessoa na instituicao (o principal primeiro). */
export default function RoleBadges({ roles }: { roles: UserRole[] }) {
  return (
    <span className="inline-flex flex-wrap gap-1">
      {roles.map((role) => (
        <span key={role} className={`rounded-full px-2 py-1 text-xs font-medium ${badgeCls(role)}`}>{roleLabels[role]}</span>
      ))}
    </span>
  );
}
