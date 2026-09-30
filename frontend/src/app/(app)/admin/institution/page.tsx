'use client';

import { useEffect, useState } from 'react';
import { BuildingLibraryIcon, MapPinIcon, PaintBrushIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import { applyBranding, institutionDisplayName, isValidBrandColor } from '@/lib/institution/branding';
import { useAuthStore } from '@/store/authStore';
import { type Campus, type Institution, type InstitutionType, institutionTypeLabels } from '@/types/institution';

const inputCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white';
const labelCls = 'block text-sm font-medium text-gray-700 dark:text-gray-300';
const sectionCls = 'rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800';
const DEFAULT_COLOR = '#4f46e5';

export default function InstitutionSettingsPage() {
  const { fetchInstitution } = useAuthStore();
  const [institution, setInstitution] = useState<Institution | null>(null);
  const [form, setForm] = useState({ name: '', legal_name: '', document: '', type: 'mixed' as InstitutionType });
  const [branding, setBranding] = useState({ display_name: '', primary_color: '', logo_url: '' });
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [newCampus, setNewCampus] = useState({ name: '', address: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<Institution>(endpoints.institutions.current)
      .then(({ data: current }) => {
        setInstitution(current);
        setForm({ name: current.name, legal_name: current.legal_name ?? '', document: current.document ?? '', type: current.type });
        setBranding({
          display_name: current.branding.display_name ?? '',
          primary_color: current.branding.primary_color ?? '',
          logo_url: current.branding.logo_url ?? '',
        });
      })
      .catch(() => toast.error('Erro ao carregar a instituição.'));
  }, []);

  const [campusReloadKey, setCampusReloadKey] = useState(0);
  const load = () => setCampusReloadKey((key) => key + 1);

  useEffect(() => {
    api.get<Campus[]>(endpoints.institutions.campuses)
      .then(({ data }) => setCampuses(data))
      .catch(() => toast.error('Erro ao carregar campi.'));
  }, [campusReloadKey]);

  // Pre-visualiza a cor enquanto edita; ao sair sem salvar, volta a cor salva.
  useEffect(() => {
    applyBranding({ primary_color: branding.primary_color });
    return () => applyBranding(useAuthStore.getState().institution?.branding);
  }, [branding.primary_color]);

  const handleSave = async () => {
    if (branding.primary_color && !isValidBrandColor(branding.primary_color)) {
      toast.error('Use uma cor no formato #RRGGBB.');
      return;
    }
    setSaving(true);
    try {
      const cleanBranding = Object.fromEntries(Object.entries(branding).filter(([, value]) => value.trim() !== ''));
      const { data } = await api.patch<Institution>(endpoints.institutions.current, {
        name: form.name,
        legal_name: form.legal_name || null,
        document: form.document || null,
        type: form.type,
        branding: cleanBranding,
      });
      setInstitution(data);
      await fetchInstitution();
      toast.success('Instituição atualizada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar instituição.'));
    } finally {
      setSaving(false);
    }
  };

  const handleCreateCampus = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post(endpoints.institutions.campuses, { name: newCampus.name, address: newCampus.address || null });
      setNewCampus({ name: '', address: '' });
      toast.success('Campus criado.');
      load();
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao criar campus.'));
    }
  };

  const toggleCampus = async (campus: Campus) => {
    try {
      await api.patch(endpoints.institutions.campus(campus.id), { is_active: !campus.is_active });
      load();
    } catch {
      toast.error('Erro ao atualizar campus.');
    }
  };

  const deleteCampus = async (campus: Campus) => {
    if (!window.confirm(`Excluir o campus "${campus.name}"?`)) return;
    try {
      await api.delete(endpoints.institutions.campus(campus.id));
      toast.success('Campus excluído.');
      load();
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao excluir campus.'));
    }
  };

  if (!institution) return <p className="text-sm text-gray-500 dark:text-gray-400">Carregando...</p>;

  const preview = institutionDisplayName({ name: form.name, branding: { display_name: branding.display_name } });

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Instituição</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Identificador: <code>{institution.slug}</code></p>
      </div>

      <section className={sectionCls}>
        <div className="mb-5 flex items-center space-x-3">
          <BuildingLibraryIcon className="h-5 w-5 text-indigo-600" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Dados</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className={labelCls}>
            Nome
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
          <label className={labelCls}>
            Tipo
            <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value as InstitutionType })} className={`${inputCls} mt-1`}>
              {Object.entries(institutionTypeLabels).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </label>
          <label className={labelCls}>
            Razão social
            <input value={form.legal_name} onChange={(e) => setForm({ ...form, legal_name: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
          <label className={labelCls}>
            CNPJ
            <input value={form.document} onChange={(e) => setForm({ ...form, document: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
        </div>
      </section>

      <section className={sectionCls}>
        <div className="mb-5 flex items-center space-x-3">
          <PaintBrushIcon className="h-5 w-5 text-indigo-600" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Identidade visual</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className={labelCls}>
            Nome exibido no menu
            <input value={branding.display_name} placeholder={form.name} onChange={(e) => setBranding({ ...branding, display_name: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
          <label className={labelCls}>
            Cor principal
            <div className="mt-1 flex gap-2">
              <input
                type="color"
                aria-label="Selecionar cor principal"
                value={isValidBrandColor(branding.primary_color) ? branding.primary_color : DEFAULT_COLOR}
                onChange={(e) => setBranding({ ...branding, primary_color: e.target.value })}
                className="h-10 w-12 cursor-pointer rounded-lg border border-gray-300 bg-white p-1 dark:border-gray-600 dark:bg-gray-900"
              />
              <input value={branding.primary_color} placeholder={DEFAULT_COLOR} onChange={(e) => setBranding({ ...branding, primary_color: e.target.value })} className={inputCls} />
            </div>
          </label>
          <label className={`${labelCls} sm:col-span-2`}>
            URL do logotipo
            <input value={branding.logo_url} placeholder="https://..." onChange={(e) => setBranding({ ...branding, logo_url: e.target.value })} className={`${inputCls} mt-1`} />
          </label>
        </div>
        <div className="mt-5 flex items-center gap-3 rounded-lg bg-gray-900 px-4 py-3">
          {branding.logo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={branding.logo_url} alt="" className="h-8 w-8 rounded-lg bg-white object-contain" />
          ) : (
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
              <span className="text-lg font-bold text-white">{preview.charAt(0).toUpperCase()}</span>
            </div>
          )}
          <span className="text-lg font-bold text-white">{preview}</span>
          <span className="ml-auto rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white">Botão</span>
        </div>
      </section>

      <div className="flex justify-end">
        <button onClick={handleSave} disabled={saving} className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-60">
          {saving ? 'Salvando...' : 'Salvar alterações'}
        </button>
      </div>

      <section className={sectionCls}>
        <div className="mb-5 flex items-center space-x-3">
          <MapPinIcon className="h-5 w-5 text-indigo-600" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Campi</h2>
        </div>
        {campuses.length === 0 ? (
          <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">Nenhum campus cadastrado. Unidades e salas podem ser vinculadas a um campus na Agenda.</p>
        ) : (
          <ul className="mb-5 divide-y divide-gray-200 dark:divide-gray-700">
            {campuses.map((campus) => (
              <li key={campus.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div className="min-w-0">
                  <p className="font-medium text-gray-900 dark:text-white">{campus.name}</p>
                  {campus.address && <p className="text-sm text-gray-500 dark:text-gray-400">{campus.address}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => toggleCampus(campus)} className={`rounded-full px-2.5 py-1 text-xs font-medium ${campus.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
                    {campus.is_active ? 'Ativo' : 'Inativo'}
                  </button>
                  <button onClick={() => deleteCampus(campus)} aria-label={`Excluir campus ${campus.name}`} className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20">
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
        <form onSubmit={handleCreateCampus} className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1.5fr_auto]">
          <input required value={newCampus.name} onChange={(e) => setNewCampus({ ...newCampus, name: e.target.value })} placeholder="Nome do campus" className={inputCls} />
          <input value={newCampus.address} onChange={(e) => setNewCampus({ ...newCampus, address: e.target.value })} placeholder="Endereço (opcional)" className={inputCls} />
          <button className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
            <PlusIcon className="h-4 w-4" /> Adicionar
          </button>
        </form>
      </section>
    </div>
  );
}
