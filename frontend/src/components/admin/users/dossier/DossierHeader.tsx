import type { ReactNode } from 'react';
import StatusBadge from '@/components/common/StatusBadge';
import RoleBadges from '@/components/admin/users/RoleBadges';
import { type User, rolesOf } from '@/types/auth';

/** Topo do cartao do dossie: nome, perfil e situacao a esquerda; acoes a direita. */
export default function DossierHeader({ user, actions }: { user: User; actions?: ReactNode }) {
  return (
    <div className="flex flex-col gap-4 border-b border-gray-200 p-5 sm:p-6 lg:flex-row lg:items-center lg:justify-between dark:border-gray-700">
      <div className="flex min-w-0 items-center gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-lg font-semibold text-white">
          {user.name.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 title={user.name} className="line-clamp-2 text-2xl font-semibold text-gray-900 dark:text-white">{user.name}</h1>
            <RoleBadges roles={rolesOf(user)} />
            <StatusBadge active={user.is_active} activeLabel="Ativo" inactiveLabel="Inativo" />
          </div>
          <p className="mt-1 truncate font-mono text-sm text-gray-500 dark:text-gray-400">#{user.id} · {user.email}</p>
        </div>
      </div>
      {actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}
    </div>
  );
}
