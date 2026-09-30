'use client';

import { useEffect, useState } from 'react';
import { ArrowRightCircleIcon, GlobeAltIcon, PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAuthStore } from '@/store/authStore';
import {
  type Institution,
  type InstitutionStatus,
  type InstitutionType,
  institutionStatusLabels,
  institutionTypeLabels,
} from '@/types/institution';

const inputCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white';
const labelCls = 'block text-sm font-medium text-gray-700 dark:text-gray-300';

const emptyForm = {
  slug: '',
  name: '',
  type: 'school' as InstitutionType,
  adminName: '',
  adminEmail: '',
  adminPassword: '',
};

function slugify(value: string) {
  return value
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);
}

export default function PlatformInstitutionsPage() {
  const { institution: current, switchInstitution } = useAuthStore();
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [slugTouched, setSlugTouched] = useState(false);
  const [creating, setCreating] = useState(false);

  const [reloadKey, setReloadKey] = useState(0);
  const load = () => setReloadKey((key) => key + 1);

  useEffect(() => {
    api.get<Institution[]>(endpoints.platform.institutions)
      .then(({ data }) => setInstitutions(data))
      .catch(() => toast.error('Erro ao carregar instituições.'))
      .finally(() => setLoading(false));
  }, [reloadKey]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const withAdmin = form.adminEmail.trim() !== '';
    setCreating(true);
    try {
      await api.post(endpoints.platform.institutions, {
        slug: form.slug,
        name: form.name,
        type: form.type,
        admin: withAdmin ? { name: form.adminName, email: form.adminEmail, password: form.adminPassword } : null,
      });
      toast.success('Instituição criada.');
      setForm(emptyForm);
      setSlugTouched(false);
      setShowForm(false);
      load();
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao criar instituição. Confira os campos.'));
    } finally {
      setCreating(false);
    }
  };

  const changeStatus = async (institution: Institution, status: InstitutionStatus) => {
    try {
      await api.patch(endpoints.platform.institution(institution.id), { status });
      toast.success('Status atualizado.');
      load();
    } catch {
      toast.error('Erro ao atualizar status.');
    }
  };

  const enter = async (institution: Institution) => {
    try {
      await switchInstitution(institution.slug);
    } catch {
      toast.error('Não foi possível entrar na instituição.');
    }
  };

  return (
    <div className="max-w-6xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <GlobeAltIcon className="h-6 w-6 text-indigo-600" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Instituições da plataforma</h1>
        </div>
        <button onClick={() => setShowForm((v) => !v)} className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
          <PlusIcon className="h-4 w-4" /> Nova instituição
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="space-y-5 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <label className={labelCls}>
              Nome
              <input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value, slug: slugTouched ? form.slug : slugify(e.target.value) })}
                className={`${inputCls} mt-1`}
              />
            </label>
            <label className={labelCls}>
              Identificador (slug)
              <input
                required
                pattern="[a-z0-9]+(-[a-z0-9]+)*"
                title="Letras minúsculas, números e hífens"
                value={form.slug}
                onChange={(e) => { setSlugTouched(true); setForm({ ...form, slug: e.target.value }); }}
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
                <input required={form.adminEmail !== ''} value={form.adminName} onChange={(e) => setForm({ ...form, adminName: e.target.value })} className={`${inputCls} mt-1`} />
              </label>
              <label className={labelCls}>
                E-mail
                <input type="email" value={form.adminEmail} onChange={(e) => setForm({ ...form, adminEmail: e.target.value })} className={`${inputCls} mt-1`} />
              </label>
              <label className={labelCls}>
                Senha inicial
                <input type="password" minLength={6} required={form.adminEmail !== ''} value={form.adminPassword} onChange={(e) => setForm({ ...form, adminPassword: e.target.value })} className={`${inputCls} mt-1`} />
              </label>
            </div>
          </fieldset>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
              Cancelar
            </button>
            <button disabled={creating} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60">
              {creating ? 'Criando...' : 'Criar instituição'}
            </button>
          </div>
        </form>
      )}

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        {loading ? (
          <p className="p-6 text-sm text-gray-500 dark:text-gray-400">Carregando...</p>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-700">
            <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 dark:bg-gray-900/40 dark:text-gray-400">
              <tr>
                <th className="px-4 py-3">Instituição</th>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Criada em</th>
                <th className="px-4 py-3"><span className="sr-only">Ações</span></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {institutions.map((institution) => (
                <tr key={institution.id}>
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900 dark:text-white">{institution.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{institution.slug}</p>
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{institutionTypeLabels[institution.type]}</td>
                  <td className="px-4 py-3">
                    <select
                      aria-label={`Status de ${institution.name}`}
                      value={institution.status}
                      onChange={(e) => changeStatus(institution, e.target.value as InstitutionStatus)}
                      className="rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
                    >
                      {Object.entries(institutionStatusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{new Date(institution.created_at).toLocaleDateString('pt-BR')}</td>
                  <td className="px-4 py-3 text-right">
                    {current?.slug === institution.slug ? (
                      <span className="text-xs font-medium text-indigo-600">Ativa agora</span>
                    ) : (
                      <button onClick={() => enter(institution)} className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700">
                        Entrar <ArrowRightCircleIcon className="h-4 w-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
