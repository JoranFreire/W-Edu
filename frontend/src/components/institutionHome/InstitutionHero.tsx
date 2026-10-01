import { institutionDisplayName } from '@/lib/institution/branding';
import { institutionTypeLabels } from '@/types/institution';
import type { InstitutionPage } from '@/types/publicSite';

/** Chamada principal: nome, frase de destaque e o caminho para a matricula. */
export default function InstitutionHero({ page }: { page: InstitutionPage }) {
  const { institution, profile, open_calls: calls } = page;
  return (
    <section className="bg-gradient-to-b from-indigo-50 to-white dark:from-gray-900 dark:to-gray-950">
      <div className="mx-auto max-w-6xl px-4 py-16 sm:py-24">
        <p className="text-sm font-semibold uppercase tracking-wide text-indigo-700 dark:text-indigo-300">{institutionTypeLabels[institution.type]}</p>
        <h1 className="mt-2 max-w-3xl text-4xl font-extrabold text-gray-900 sm:text-5xl dark:text-white">{institutionDisplayName(institution)}</h1>
        {profile.tagline && <p className="mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-300">{profile.tagline}</p>}
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          {calls.length > 0 ? (
            <a href="#inscricoes" className="rounded-lg bg-indigo-600 px-6 py-3 text-center font-semibold text-white hover:bg-indigo-700">
              {calls.length === 1 ? 'Inscrição aberta: inscreva-se' : `${calls.length} inscrições abertas`}
            </a>
          ) : (
            <a href="#matricula" className="rounded-lg bg-indigo-600 px-6 py-3 text-center font-semibold text-white hover:bg-indigo-700">Como se matricular</a>
          )}
          <a href="#cursos" className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-center font-semibold text-gray-800 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100">Conheça os cursos</a>
        </div>
      </div>
    </section>
  );
}
