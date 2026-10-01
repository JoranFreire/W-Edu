import Link from 'next/link';
import { institutionDisplayName } from '@/lib/institution/branding';
import type { InstitutionSummary } from '@/types/institution';

/** Topo da pagina da instituicao: marca e acesso a area do aluno e da equipe. */
export default function InstitutionHeader({ institution, homeHref }: { institution: InstitutionSummary; homeHref: string }) {
  const name = institutionDisplayName(institution);
  return (
    <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link href={homeHref} className="flex min-w-0 items-center gap-3">
          {institution.branding?.logo_url
            // eslint-disable-next-line @next/next/no-img-element -- logo de dominio externo cadastrado pela instituicao
            ? <img src={institution.branding.logo_url} alt="" className="h-9 w-auto max-w-32 object-contain" />
            : <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 font-bold text-white">{name.charAt(0)}</span>}
          <span className="truncate font-semibold text-gray-900 dark:text-white">{name}</span>
        </Link>
        <Link href="/login" className="shrink-0 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">Área do aluno</Link>
      </div>
    </header>
  );
}
