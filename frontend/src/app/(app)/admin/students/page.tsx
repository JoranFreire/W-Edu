'use client';

import { useState } from 'react';
import { BuildingOfficeIcon, PlusIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import EditOrganizationModal from '@/components/admin/EditOrganizationModal';
import EditUserModal from '@/components/admin/EditUserModal';
import NewUserModal from '@/components/admin/NewUserModal';
import OrganizationsSection from '@/components/admin/OrganizationsSection';
import UsersList from '@/components/admin/UsersList';
import UsersFilterBar from '@/components/admin/users/UsersFilterBar';
import NewOrganizationModal from '@/components/admin/people/NewOrganizationModal';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { apiErrorMessage } from '@/lib/api/errors';
import { type NewUserInput, type OrganizationInput, type UserUpdateInput, usePeople } from '@/lib/hooks/admin/usePeople';
import { useUserFilters } from '@/lib/hooks/admin/useUserFilters';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { assignableRoles, canManageUser } from '@/lib/users/rolePolicy';
import { useAuthStore } from '@/store/authStore';
import { type Organization, type User, isAdminRole } from '@/types/auth';

type PeopleTab = 'users' | 'organizations';
type Dialog =
  | { kind: 'newUser' }
  | { kind: 'editUser'; user: User }
  | { kind: 'deleteUser'; user: User }
  | { kind: 'newOrganization' }
  | { kind: 'editOrganization'; organization: Organization }
  | null;

export default function AdminStudentsPage() {
  const { student } = useAuthStore();
  const isAdmin = isAdminRole(student?.role);
  const people = usePeople();
  const [activeTab, setActiveTab] = useState<PeopleTab>('users');
  const [dialog, setDialog] = useState<Dialog>(null);
  const filters = useUserFilters(people.users);
  useErrorToast(people.error, 'Erro ao carregar usuários.');

  const close = () => setDialog(null);
  // Executa a acao, avisa o resultado e fecha o dialogo em caso de sucesso.
  const run = async (action: () => Promise<void>, success: string, failure: string) => {
    try {
      await action();
      toast.success(success);
      close();
    } catch (error) { toast.error(apiErrorMessage(error, failure)); }
  };

  const createUser = (input: NewUserInput) => run(() => people.createUser(input), 'Usuário criado!', 'Erro ao criar usuário.');
  const updateUser = (id: number, input: UserUpdateInput) => run(() => people.updateUser(id, input), 'Usuário atualizado.', 'Erro ao atualizar usuário.');
  const deleteUser = (user: User) => run(() => people.deleteUser(user.id), 'Usuário excluído.', 'Erro ao excluir usuário.');
  const createOrganization = (input: OrganizationInput) => run(() => people.createOrganization(input), 'Empresa criada!', 'Erro ao criar empresa.');
  const updateOrganization = (id: number, input: OrganizationInput) => run(() => people.updateOrganization(id, input), 'Empresa atualizada.', 'Erro ao atualizar empresa.');

  if (people.loading && people.users.length === 0) return <Spinner />;

  const roles = assignableRoles(student?.role);
  const tabs: TabItem<PeopleTab>[] = [
    { id: 'users', label: 'Usuários', icon: UserGroupIcon, badge: people.users.length },
    { id: 'organizations', label: 'Empresas', icon: BuildingOfficeIcon, badge: people.organizations.length },
  ];
  const userCount = people.users.length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Usuários</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{userCount} usuário{userCount !== 1 ? 's' : ''} cadastrado{userCount !== 1 ? 's' : ''}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {activeTab === 'users' && (
            <button onClick={() => setDialog({ kind: 'newUser' })} className="flex items-center justify-center space-x-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
              <PlusIcon className="w-4 h-4" /><span>Novo usuário</span>
            </button>
          )}
          {activeTab === 'organizations' && isAdmin && (
            <button onClick={() => setDialog({ kind: 'newOrganization' })} className="flex items-center justify-center space-x-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
              <PlusIcon className="w-4 h-4" /><span>Nova empresa</span>
            </button>
          )}
        </div>
      </div>

      <div className="space-y-5">
        <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Usuários e empresas" idPrefix="people" />
        <div id={`people-${activeTab}`} role="tabpanel">
          {activeTab === 'users' && (
            <div className="space-y-4">
              <UsersFilterBar filter={filters.filter} onFilter={filters.setFilter} counts={filters.counts} query={filters.query} onQuery={filters.setQuery} />
              <UsersList
                users={filters.filtered}
                filtered={people.users.length > 0}
                organizations={people.organizations}
                canDelete={isAdmin}
                canManageUser={(user) => canManageUser(student?.role, user)}
                onEdit={(user) => setDialog({ kind: 'editUser', user })}
                onDelete={(id) => {
                  const user = people.users.find((item) => item.id === id);
                  if (user) setDialog({ kind: 'deleteUser', user });
                }}
              />
            </div>
          )}
          {activeTab === 'organizations' && (
            <OrganizationsSection organizations={people.organizations} isAdmin={isAdmin} showCreateForm={false} onCreated={people.reload}
              onEdit={(organization) => setDialog({ kind: 'editOrganization', organization })} />
          )}
        </div>
      </div>

      {dialog?.kind === 'newUser' && <NewUserModal organizations={people.organizations} availableRoles={roles} onClose={close} onSave={createUser} />}
      {dialog?.kind === 'editUser' && <EditUserModal user={dialog.user} organizations={people.organizations} availableRoles={roles} onClose={close} onSave={updateUser} />}
      {dialog?.kind === 'deleteUser' && (
        <ConfirmDialog
          title="Excluir usuário"
          message={`Deseja excluir "${dialog.user.name}"?`}
          confirmLabel="Excluir"
          danger
          onCancel={close}
          onConfirm={() => deleteUser(dialog.user)}
        />
      )}
      {dialog?.kind === 'newOrganization' && <NewOrganizationModal onSave={createOrganization} onClose={close} />}
      {dialog?.kind === 'editOrganization' && <EditOrganizationModal organization={dialog.organization} onClose={close} onSave={updateOrganization} />}
    </div>
  );
}
