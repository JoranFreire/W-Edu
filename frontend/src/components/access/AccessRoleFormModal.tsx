'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { groupByModule } from '@/lib/access/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { AccessRole, AccessRoleInput, PermissionDef } from '@/types/access';

/** Cria ou edita perfil; so aparecem habilitadas as permissoes que o proprio usuario tem. */
export default function AccessRoleFormModal({ role, catalog, grantable, onSave, onClose }: {
  role?: AccessRole;
  catalog: PermissionDef[];
  grantable: string[];
  onSave: (input: AccessRoleInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState<AccessRoleInput>({
    name: role?.name ?? '', description: role?.description ?? null, permissions: role?.permissions ?? [],
  });
  const { saving, run } = useSubmitting();
  const toggle = (key: string) => setForm({
    ...form, permissions: form.permissions.includes(key) ? form.permissions.filter((item) => item !== key) : [...form.permissions, key],
  });
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave(form)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar o perfil.')));
  };
  return (
    <Modal title={role ? `Editar: ${role.name}` : 'Novo perfil de acesso'} size="xl" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Nome<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Descrição
          <input value={form.description ?? ''} onChange={(e) => setForm({ ...form, description: e.target.value || null })} className={`mt-1 ${inputCls}`} />
        </label>
        {groupByModule(catalog).map(([module, permissions]) => (
          <fieldset key={module} className="space-y-2">
            <legend className="text-sm font-semibold text-gray-900 dark:text-white">{module}</legend>
            {permissions.map((permission) => {
              const allowed = grantable.includes(permission.key);
              return (
                <label key={permission.key} className={`flex items-start gap-2 text-sm ${allowed ? 'text-gray-800 dark:text-gray-200' : 'text-gray-400'}`}>
                  <input type="checkbox" disabled={!allowed} checked={form.permissions.includes(permission.key)} onChange={() => toggle(permission.key)} className="mt-1" />
                  <span><span className="font-medium">{permission.label}</span> — {permission.description}</span>
                </label>
              );
            })}
          </fieldset>
        ))}
        <FormActions saving={saving} onCancel={onClose} />
      </form>
    </Modal>
  );
}
