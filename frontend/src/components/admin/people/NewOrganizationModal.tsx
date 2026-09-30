'use client';

import { useState } from 'react';
import Modal from '@/components/common/Modal';
import type { OrganizationInput } from '@/lib/hooks/admin/usePeople';

const inputCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white';

export default function NewOrganizationModal({ onSave, onClose }: {
  onSave: (input: OrganizationInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState({ name: '', legalName: '', document: '', contactEmail: '' });

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSave({
      name: form.name,
      legal_name: form.legalName || null,
      document: form.document || null,
      contact_email: form.contactEmail || null,
    });
  };

  return (
    <Modal title="Nova empresa" description="Cadastre uma organização B2B." size="sm" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} required placeholder="Nome da empresa" className={inputCls} />
        <input value={form.legalName} onChange={(e) => setForm((p) => ({ ...p, legalName: e.target.value }))} placeholder="Razão social" className={inputCls} />
        <input value={form.document} onChange={(e) => setForm((p) => ({ ...p, document: e.target.value }))} placeholder="Documento" className={inputCls} />
        <input type="email" value={form.contactEmail} onChange={(e) => setForm((p) => ({ ...p, contactEmail: e.target.value }))} placeholder="E-mail de contato" className={inputCls} />
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">Cancelar</button>
          <button className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">Criar empresa</button>
        </div>
      </form>
    </Modal>
  );
}
