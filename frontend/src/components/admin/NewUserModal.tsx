'use client';

import { useState } from 'react';
import RolesField, { type RolesValue } from '@/components/admin/users/RolesField';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import type { NewUserInput } from '@/lib/hooks/admin/usePeople';
import type { RoleOption } from '@/lib/users/rolePolicy';
import type { Organization } from '@/types/auth';

/** Cadastro de usuario com um ou mais papeis (aluno e professor, por exemplo). */
export default function NewUserModal({ organizations, availableRoles, onClose, onSave }: {
  organizations: Organization[];
  availableRoles: RoleOption[];
  onClose: () => void;
  onSave: (data: NewUserInput) => Promise<void>;
}) {
  const [form, setForm] = useState({ name: '', email: '', password: '', organizationId: '' });
  const [roles, setRoles] = useState<RolesValue>({ roles: ['student'], primary: 'student' });
  const [saving, setSaving] = useState(false);
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    await onSave({
      name: form.name, email: form.email, password: form.password,
      role: roles.primary, roles: roles.roles, organization_id: form.organizationId || null,
    });
    setSaving(false);
  };

  return (
    <Modal title="Novo usuário" size="lg" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Nome *<input required value={form.name} onChange={(e) => set({ name: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>E-mail *<input required type="email" value={form.email} onChange={(e) => set({ email: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Senha *<input required type="password" minLength={6} value={form.password} onChange={(e) => set({ password: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <RolesField options={availableRoles} value={roles} onChange={setRoles} />
        <label className={labelCls}>Empresa
          <select value={form.organizationId} onChange={(e) => set({ organizationId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Sem empresa</option>
            {organizations.map((organization) => <option key={organization.id} value={organization.id}>{organization.name}</option>)}
          </select>
        </label>
        <FormActions saving={saving} disabled={roles.roles.length === 0} onCancel={onClose} submitLabel="Criar usuário" />
      </form>
    </Modal>
  );
}
