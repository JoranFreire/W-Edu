'use client';

import { useEffect, useState } from 'react';
import { BuildingLibraryIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import { institutionDisplayName } from '@/lib/institution/branding';
import { useAuthStore } from '@/store/authStore';
import type { InstitutionSummary } from '@/types/institution';

export function InstitutionSwitcher() {
  const { student, institution, memberships, switchInstitution } = useAuthStore();
  const [platformInstitutions, setPlatformInstitutions] = useState<InstitutionSummary[]>([]);
  const [switching, setSwitching] = useState(false);
  const isSuperAdmin = student?.role === 'super_admin';
  // Super admin pode entrar em qualquer instituicao; os demais, nas que sao membros.
  const options = isSuperAdmin ? platformInstitutions : memberships.map((membership) => membership.institution);

  useEffect(() => {
    if (!isSuperAdmin) return;
    api.get<InstitutionSummary[]>(endpoints.platform.institutions)
      .then((response) => setPlatformInstitutions(response.data))
      .catch(() => setPlatformInstitutions([]));
  }, [isSuperAdmin]);

  if (!institution) return null;

  const label = institutionDisplayName(institution);
  if (options.length < 2) {
    return (
      <span className="hidden max-w-[12rem] items-center gap-1.5 truncate text-sm text-gray-600 dark:text-gray-300 md:flex" title={label}>
        <BuildingLibraryIcon className="h-4 w-4 flex-shrink-0 text-indigo-600" />
        <span className="truncate">{label}</span>
      </span>
    );
  }

  const handleChange = async (slug: string) => {
    if (slug === institution.slug) return;
    setSwitching(true);
    try {
      await switchInstitution(slug);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Não foi possível trocar de instituição.'));
      setSwitching(false);
    }
  };

  return (
    <label className="flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300">
      <BuildingLibraryIcon className="h-4 w-4 flex-shrink-0 text-indigo-600" />
      <span className="sr-only">Instituição ativa</span>
      <select
        value={institution.slug}
        disabled={switching}
        onChange={(e) => handleChange(e.target.value)}
        className="max-w-[10rem] truncate rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white sm:max-w-[14rem]"
      >
        {options.map((option) => (
          <option key={option.slug} value={option.slug}>{institutionDisplayName(option)}</option>
        ))}
      </select>
    </label>
  );
}
