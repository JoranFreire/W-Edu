'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { apiErrorMessage } from '@/lib/api/errors';
import type { NewInstitutionInput } from '@/lib/hooks/platform/usePlatformInstitutions';
import { slugify } from '@/lib/text/slugify';
import { type InstitutionType, institutionTypeLabels } from '@/types/institution';

const inputCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white';
const labelCls = 'block text-sm font-medium text-gray-700 dark:text-gray-300';

const empty = { slug: '', name: '', type: 'school' as InstitutionType, adminName: '', adminEmail: '', adminPassword: '' };

/** Cria instituicao com slug sugerido a partir do nome e, opcionalmente, o primeiro admin. */
export default function CreateInstitutionForm({ onCreate, onCancel }: {
  onCreate: (input: NewInstitutionInput) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState(empty);
  const [slugEdited, setSlugEdited] = useState(false);
  const [creating, setCreating] = useState(false);
  const withAdmin = form.adminEmail.trim() !== '';

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setCreating(true);
    try {
      await onCreate({
        slug: form.slug,
        name: form.name,
        type: form.type,
        admin: withAdmin ? { name: form.adminName, email: form.adminEmail, password: form.adminPassword } : null,
      });
      toast.success('Instituição criada.');
      setForm(empty);
      setSlugEdited(false);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao criar instituição. Confira os campos.'));
    } finally {
      setCreating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <label className={labelCls}>
          Nome
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value, slug: slugEdited ? form.slug : slugify(e.target.value) })} className={`${inputCls} mt-1`} />
        </label>
        <label className={labelCls}>
          Identificador (slug)
          <input
            required
            pattern="[a-z0-9]+(-[a-z0-9]+)*"
            title="Letras minúsculas, números e hífens"
            value={form.slug}
            onChange={(e) => { setSlugEdited(true); setForm({ ...form, slug: e.target.value }); }}
            className={`${inputCls} mt-1`}
          />
        </label>
        <label className={labelCls}>
          Tipo
          <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value as InstitutionType })} className={`${inputCls} mt-1`}>
            {Object.entries(institutionTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
      </div>
      <fieldset>
        <legend className="text-sm font-semibold text-gray-900 dark:text-white">Primeiro administrador (opcional)</legend>
        <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <label className={labelCls}>
            Nome
            <input required={withAdmin} value={form.adminName} onChange={(e) => setForm({ ...form, adminName: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
          <label className={labelCls}>
            E-mail
            <input type="email" value={form.adminEmail} onChange={(e) => setForm({ ...form, adminEmail: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
          <label className={labelCls}>
            Senha inicial
            <input type="password" minLength={6} required={withAdmin} value={form.adminPassword} onChange={(e) => setForm({ ...form, adminPassword: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
        </div>
      </fieldset>
      <div className="flex justify-end gap-3">
        <button type="button" onClick={onCancel} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
          Cancelar
        </button>
        <button disabled={creating} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60">
          {creating ? 'Criando...' : 'Criar instituição'}
        </button>
      </div>
    </form>
  );
}
