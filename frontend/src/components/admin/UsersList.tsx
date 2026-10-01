'use client';

import Link from 'next/link';
import { ChevronRightIcon, PencilIcon, TrashIcon, UsersIcon } from '@heroicons/react/24/outline';
import RoleBadges from '@/components/admin/users/RoleBadges';
import { type Organization, type User, rolesOf } from '@/types/auth';

/** Lista de usuarios; o nome abre o dossie da pessoa. */
export default function UsersList({ users, organizations, canDelete, canManageUser, onEdit, onDelete, filtered = false }: {
  users: User[];
  organizations: Organization[];
  canDelete: boolean;
  canManageUser: (user: User) => boolean;
  onEdit: (user: User) => void;
  onDelete: (id: string) => void;
  /** Lista vazia por causa do filtro (e nao por falta de cadastro). */
  filtered?: boolean;
}) {
  if (users.length === 0 && filtered) {
    return (
      <div className="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center text-sm text-gray-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400">
        Nenhum usuário encontrado com esse filtro.
      </div>
    );
  }
  if (users.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-gray-300 bg-white p-10 text-center dark:border-gray-600 dark:bg-gray-800">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700">
          <UsersIcon className="h-6 w-6 text-gray-400" />
        </div>
        <p className="text-gray-900 dark:text-white">Nenhum usuário cadastrado.</p>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Crie o primeiro usuário para começar a gestão.</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700">
      {users.map((user) => (
        <div key={user.id} className="flex items-center justify-between px-5 py-4">
          <Link href={`/admin/users/${user.id}`} aria-label={`Dossiê de ${user.name}`} className="group flex min-w-0 items-center space-x-4">
            <div className="w-9 h-9 shrink-0 bg-indigo-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">{user.name.charAt(0).toUpperCase()}</span>
            </div>
            <div className="min-w-0">
              <p className="flex items-center gap-1 text-sm font-medium text-gray-900 group-hover:text-indigo-700 dark:text-white dark:group-hover:text-indigo-300">
                {user.name}<ChevronRightIcon className="h-3.5 w-3.5 opacity-0 transition-opacity group-hover:opacity-100" />
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user.email}{user.organization_id ? ` · ${organizations.find((o) => o.id === user.organization_id)?.name ?? 'Empresa'}` : ''}
              </p>
            </div>
          </Link>
          <div className="flex items-center space-x-3">
            <RoleBadges roles={rolesOf(user)} />
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${user.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
              {user.is_active ? 'Ativo' : 'Inativo'}
            </span>
            <p className="text-xs text-gray-400 hidden sm:block">{new Date(user.created_at).toLocaleDateString('pt-BR')}</p>
            {canManageUser(user) && (
              <>
                <button onClick={() => onEdit(user)} aria-label={`Editar ${user.name}`} className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors">
                  <PencilIcon className="w-4 h-4" />
                </button>
                {canDelete && (
                  <button onClick={() => onDelete(user.id)} aria-label={`Excluir ${user.name}`} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors">
                    <TrashIcon className="w-4 h-4" />
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
