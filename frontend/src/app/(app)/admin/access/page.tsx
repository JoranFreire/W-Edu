'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import AccessRoleCard from '@/components/access/AccessRoleCard';
import AccessRoleFormModal from '@/components/access/AccessRoleFormModal';
import SectionHeader from '@/components/common/SectionHeader';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { roleLabels } from '@/lib/access/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAccessAdmin } from '@/lib/hooks/access/useAccessAdmin';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import type { AccessRole, AccessRoleInput } from '@/types/access';

/** Perfis de acesso (RBAC): perfis padrao dos papeis e perfis personalizados da instituicao. */
export default function AccessPage() {
  const permissions = useAuthStore((state) => state.permissions);
  const { data, error, save, remove, assign, unassign } = useAccessAdmin();
  const [editing, setEditing] = useState<AccessRole | 'new' | null>(null);
  useErrorToast(error, 'Erro ao carregar os perfis de acesso.');

  const run = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir.'));
    }
  };
  const handleSave = async (input: AccessRoleInput) => {
    await save(editing === 'new' || editing === null ? null : editing.id, input);
    toast.success('Perfil salvo.');
    setEditing(null);
  };

  if (!data) return <Spinner />;
  const label = (key: string) => data.catalog.find((permission) => permission.key === key)?.label ?? key;
  return (
    <div className="space-y-6">
      <section className={`${sectionCls} space-y-4`}>
        <SectionHeader title="Perfis de acesso" description="Some permissões a qualquer pessoa da instituição. Só é possível conceder o que você mesmo pode fazer."
          actionLabel="Novo perfil" onAction={() => setEditing('new')} />
        {data.roles.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum perfil personalizado.</p> : (
          <ul className="space-y-3">
            {data.roles.map((role) => (
              <AccessRoleCard key={role.id} role={role} catalog={data.catalog} members={data.members}
                onEdit={() => setEditing(role)}
                onRemove={() => globalThis.confirm(`Excluir o perfil ${role.name}?`) && run(() => remove(role.id), 'Perfil excluído.')}
                onAssign={(userId) => run(() => assign(role.id, userId), 'Perfil atribuído.')}
                onUnassign={(userId) => run(() => unassign(role.id, userId), 'Perfil removido da pessoa.')} />
            ))}
          </ul>
        )}
      </section>
      <section className={`${sectionCls} space-y-3`}>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Perfis padrão dos papéis</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Cada papel de usuário já vem com estas permissões.</p>
        <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
          {data.builtIn.map((profile) => (
            <li key={profile.role} className="py-2 text-gray-800 dark:text-gray-200">
              <strong className="text-gray-900 dark:text-white">{roleLabels[profile.role] ?? profile.role}</strong>:{' '}
              {profile.permissions.length ? profile.permissions.map(label).join(', ') : 'nenhuma permissão administrativa'}
            </li>
          ))}
        </ul>
      </section>
      {editing && (
        <AccessRoleFormModal role={editing === 'new' ? undefined : editing} catalog={data.catalog} grantable={permissions}
          onSave={handleSave} onClose={() => setEditing(null)} />
      )}
    </div>
  );
}
