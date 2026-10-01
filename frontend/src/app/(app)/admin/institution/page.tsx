'use client';

import CampusesSection from '@/components/admin/institution/CampusesSection';
import InstitutionSettingsForm from '@/components/admin/institution/InstitutionSettingsForm';
import PublicPageSection from '@/components/admin/institution/PublicPageSection';
import CurrentPlanSection from '@/components/saas/CurrentPlanSection';
import Spinner from '@/components/common/Spinner';
import { useCurrentInstitution } from '@/lib/hooks/admin/useCurrentInstitution';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function InstitutionSettingsPage() {
  const { institution, error, save, savePublicProfile } = useCurrentInstitution();
  useErrorToast(error, 'Erro ao carregar a instituição.');

  if (!institution) return error ? null : <Spinner />;

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Instituição</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Identificador: <code>{institution.slug}</code></p>
      </div>
      <InstitutionSettingsForm key={institution.id} institution={institution} onSave={save} />
      <PublicPageSection key={`page-${institution.id}`} institution={institution} onSave={savePublicProfile} />
      <CampusesSection />
      <CurrentPlanSection />
    </div>
  );
}
