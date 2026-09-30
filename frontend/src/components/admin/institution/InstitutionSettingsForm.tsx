'use client';

import { useState } from 'react';
import { BuildingLibraryIcon, PaintBrushIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { apiErrorMessage } from '@/lib/api/errors';
import type { InstitutionInput } from '@/lib/hooks/admin/useCurrentInstitution';
import { useBrandColorPreview } from '@/lib/hooks/useBrandColorPreview';
import { institutionDisplayName, isValidBrandColor } from '@/lib/institution/branding';
import type { Institution } from '@/types/institution';
import BrandingFields, { type BrandingValues } from './BrandingFields';
import BrandingPreview from './BrandingPreview';
import InstitutionDataFields, { type InstitutionDataValues } from './InstitutionDataFields';
import { sectionCls } from '@/components/common/formStyles';

function SectionTitle({ icon: Icon, title }: { icon: typeof BuildingLibraryIcon; title: string }) {
  return (
    <div className="mb-5 flex items-center space-x-3">
      <Icon className="h-5 w-5 text-indigo-600" />
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h2>
    </div>
  );
}

/** Edita dados e identidade visual da instituicao; inicia com os valores salvos. */
export default function InstitutionSettingsForm({ institution, onSave }: {
  institution: Institution;
  onSave: (input: InstitutionInput) => Promise<void>;
}) {
  const [data, setData] = useState<InstitutionDataValues>({
    name: institution.name,
    legal_name: institution.legal_name ?? '',
    document: institution.document ?? '',
    type: institution.type,
  });
  const [branding, setBranding] = useState<BrandingValues>({
    display_name: institution.branding.display_name ?? '',
    primary_color: institution.branding.primary_color ?? '',
    logo_url: institution.branding.logo_url ?? '',
  });
  const [saving, setSaving] = useState(false);
  useBrandColorPreview(branding.primary_color);

  const handleSave = async () => {
    if (branding.primary_color && !isValidBrandColor(branding.primary_color)) {
      toast.error('Use uma cor no formato #RRGGBB.');
      return;
    }
    setSaving(true);
    try {
      await onSave({
        name: data.name,
        legal_name: data.legal_name || null,
        document: data.document || null,
        type: data.type,
        branding: Object.fromEntries(Object.entries(branding).filter(([, value]) => value.trim() !== '')),
      });
      toast.success('Instituição atualizada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar instituição.'));
    } finally {
      setSaving(false);
    }
  };

  const previewName = institutionDisplayName({ name: data.name, branding: { display_name: branding.display_name } });

  return (
    <>
      <section className={sectionCls}>
        <SectionTitle icon={BuildingLibraryIcon} title="Dados" />
        <InstitutionDataFields values={data} onChange={setData} />
      </section>
      <section className={sectionCls}>
        <SectionTitle icon={PaintBrushIcon} title="Identidade visual" />
        <BrandingFields values={branding} namePlaceholder={data.name} onChange={setBranding} />
        <BrandingPreview name={previewName} logoUrl={branding.logo_url} />
      </section>
      <div className="flex justify-end">
        <button onClick={handleSave} disabled={saving} className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-60">
          {saving ? 'Salvando...' : 'Salvar alterações'}
        </button>
      </div>
    </>
  );
}
