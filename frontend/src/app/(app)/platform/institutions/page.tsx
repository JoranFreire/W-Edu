'use client';

import { useState } from 'react';
import { GlobeAltIcon, PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import CreateInstitutionForm from '@/components/platform/CreateInstitutionForm';
import DomainModal from '@/components/platform/DomainModal';
import InstitutionsTable from '@/components/platform/InstitutionsTable';
import { type NewInstitutionInput, usePlatformInstitutions } from '@/lib/hooks/platform/usePlatformInstitutions';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import type { Institution, InstitutionStatus } from '@/types/institution';

export default function PlatformInstitutionsPage() {
  const { institution: current, switchInstitution } = useAuthStore();
  const platform = usePlatformInstitutions();
  const [showForm, setShowForm] = useState(false);
  const [editingDomain, setEditingDomain] = useState<Institution | null>(null);
  useErrorToast(platform.error, 'Erro ao carregar instituições.');

  const create = async (input: NewInstitutionInput) => {
    await platform.create(input);
    setShowForm(false);
  };

  const changeStatus = async (institution: Institution, status: InstitutionStatus) => {
    try {
      await platform.setStatus(institution, status);
      toast.success('Status atualizado.');
    } catch { toast.error('Erro ao atualizar status.'); }
  };

  const enter = async (institution: Institution) => {
    try { await switchInstitution(institution.slug); } catch { toast.error('Não foi possível entrar na instituição.'); }
  };

  return (
    <div className="max-w-6xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <GlobeAltIcon className="h-6 w-6 text-indigo-600" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Instituições da plataforma</h1>
        </div>
        <button onClick={() => setShowForm((visible) => !visible)} className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
          <PlusIcon className="h-4 w-4" /> Nova instituição
        </button>
      </div>

      {showForm && <CreateInstitutionForm onCreate={create} onCancel={() => setShowForm(false)} />}

      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        {platform.loading && platform.institutions.length === 0 ? (
          <p className="p-6 text-sm text-gray-500 dark:text-gray-400">Carregando...</p>
        ) : (
          <InstitutionsTable institutions={platform.institutions} activeSlug={current?.slug} onStatusChange={changeStatus} onEnter={enter} onDomain={setEditingDomain} />
        )}
      </div>
      {editingDomain && (
        <DomainModal key={editingDomain.id} institution={editingDomain} onSave={(domain) => platform.setDomain(editingDomain, domain)} onClose={() => setEditingDomain(null)} />
      )}
    </div>
  );
}
