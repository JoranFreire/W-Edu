'use client';

import { useState } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { GlobeAltIcon } from '@heroicons/react/24/outline';
import { inputCls, labelCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { Institution } from '@/types/institution';
import type { PublicProfile } from '@/types/publicSite';

const FIELDS: { key: keyof PublicProfile; label: string; placeholder?: string; long?: boolean }[] = [
  { key: 'tagline', label: 'Frase de destaque', placeholder: 'Ex.: Formação técnica que abre portas' },
  { key: 'about', label: 'Sobre a instituição', long: true },
  { key: 'enrollment_info', label: 'Como se matricular', placeholder: 'Documentos, períodos de matrícula, valores…', long: true },
  { key: 'phone', label: 'Telefone' },
  { key: 'whatsapp', label: 'WhatsApp' },
  { key: 'email', label: 'E-mail' },
  { key: 'website', label: 'Site' },
  { key: 'instagram', label: 'Instagram', placeholder: '@instituicao' },
  { key: 'address', label: 'Endereço' },
];

/** Conteudo da pagina publica da instituicao (a que aparece no dominio dela, com as matriculas). */
export default function PublicPageSection({ institution, onSave }: {
  institution: Institution;
  onSave: (profile: PublicProfile) => Promise<void>;
}) {
  const [draft, setDraft] = useState<PublicProfile>(institution.public_profile ?? {});
  const { saving, run } = useSubmitting();

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    // Campo vazio vira ausente (a API limpa o que nao vier).
    const profile = Object.fromEntries(Object.entries(draft).filter(([, value]) => typeof value === 'string' && value.trim() !== '')) as PublicProfile;
    run(() => onSave(profile)).then(() => toast.success('Página pública atualizada.'))
      .catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar a página pública.')));
  };

  return (
    <section aria-label="Página pública" className={sectionCls}>
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 font-semibold text-gray-900 dark:text-white"><GlobeAltIcon className="h-5 w-5 text-indigo-600" />Página pública</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {institution.custom_domain
              ? <>Publicada em <strong>{institution.custom_domain}</strong>, com os cursos e as inscrições abertas.</>
              : 'Mostra os cursos e as inscrições abertas. Para usar o domínio da instituição, fale com o suporte da plataforma.'}
          </p>
        </div>
        <Link href={`/instituicao/${institution.slug}`} target="_blank" className="shrink-0 text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">Ver página →</Link>
      </div>
      <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
        {FIELDS.map(({ key, label, placeholder, long }) => (
          <label key={key} className={`${labelCls} ${long ? 'sm:col-span-2' : ''}`}>{label}
            {long
              ? <textarea rows={4} value={draft[key] ?? ''} placeholder={placeholder} onChange={(e) => setDraft({ ...draft, [key]: e.target.value })} className={`mt-1 ${inputCls}`} />
              : <input type={key === 'email' ? 'email' : 'text'} value={draft[key] ?? ''} placeholder={placeholder} onChange={(e) => setDraft({ ...draft, [key]: e.target.value })} className={`mt-1 ${inputCls}`} />}
          </label>
        ))}
        <div className="sm:col-span-2">
          <button type="submit" disabled={saving} className={primaryButtonCls}>{saving ? 'Salvando...' : 'Salvar página pública'}</button>
        </div>
      </form>
    </section>
  );
}
