'use client';

import { useState } from 'react';
import BirthDateField from '@/components/admin/users/BirthDateField';
import RolesField, { type RolesValue } from '@/components/admin/users/RolesField';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import type { UserUpdateInput } from '@/lib/hooks/admin/usePeople';
import type { RoleOption } from '@/lib/users/rolePolicy';
import { type Organization, type User, rolesOf } from '@/types/auth';

/** Edicao de usuario; papeis que a pessoa logada nao atribui (ex.: responsavel) ficam como estao. */
export default function EditUserModal({ user, organizations, availableRoles, onClose, onSave }: {
  user: User;
  organizations: Organization[];
  availableRoles: RoleOption[];
  onClose: () => void;
  onSave: (id: string, data: UserUpdateInput) => Promise<void>;
}) {
  const assignable = availableRoles.map(([role]) => role);
  const current = rolesOf(user);
  const locked = current.filter((role) => !assignable.includes(role));
  const [form, setForm] = useState({ name: user.name, email: user.email, organizationId: user.organization_id ?? '', isActive: user.is_active, birthDate: user.birth_date ?? '' });
  const [roles, setRoles] = useState<RolesValue>({ roles: current.filter((role) => assignable.includes(role)), primary: user.role });
  const [saving, setSaving] = useState(false);
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    await onSave(user.id, {
      name: form.name, email: form.email, organization_id: form.organizationId || null, is_active: form.isActive,
      birth_date: form.birthDate || null,
      role: roles.primary, roles: [...roles.roles, ...locked],
    });
    setSaving(false);
  };

  return (
    <Modal title="Editar usuário" size="lg" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Nome *<input required value={form.name} onChange={(e) => set({ name: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>E-mail *<input required type="email" value={form.email} onChange={(e) => set({ email: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <BirthDateField value={form.birthDate} onChange={(birthDate) => set({ birthDate })} />
        <RolesField options={availableRoles} value={roles} locked={locked} onChange={setRoles} />
        <label className={labelCls}>Empresa
          <select value={form.organizationId} onChange={(e) => set({ organizationId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Sem empresa</option>
            {organizations.map((organization) => <option key={organization.id} value={organization.id}>{organization.name}</option>)}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input type="checkbox" checked={form.isActive} onChange={(e) => set({ isActive: e.target.checked })} className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
          Usuário ativo
        </label>
        <FormActions saving={saving} disabled={roles.roles.length + locked.length === 0} onCancel={onClose} submitLabel="Salvar usuário" />
      </form>
    </Modal>
  );
}
