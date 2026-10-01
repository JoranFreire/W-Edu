import { programLevelLabels } from '@/lib/academic/labels';
import { courseModalityLabels } from '@/lib/courses/labels';
import type { ProgramLevel } from '@/types/academic';
import type { InstitutionPage } from '@/types/publicSite';

type Props = Pick<InstitutionPage, 'programs' | 'courses'>;

/** O que a instituicao oferece: programas (etapas, cursos tecnicos, graduacao) e cursos livres/online. */
export default function OfferingsSection({ programs, courses }: Props) {
  if (programs.length === 0 && courses.length === 0) return null;
  return (
    <section id="cursos" aria-label="Cursos" className="scroll-mt-6 bg-gray-50 py-14 dark:bg-gray-900/60">
      <div className="mx-auto max-w-6xl px-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Cursos</h2>
        {programs.length > 0 && (
          <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {programs.map((program) => (
              <article key={program.id} className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
                <p className="text-xs font-semibold uppercase text-indigo-700 dark:text-indigo-300">{programLevelLabels[program.level as ProgramLevel] ?? program.level}</p>
                <h3 className="mt-1 font-semibold text-gray-900 dark:text-white">{program.name}</h3>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {[program.degree, program.duration_terms ? `${program.duration_terms} períodos` : null, program.total_hours ? `${program.total_hours} h` : null].filter(Boolean).join(' · ')}
                </p>
              </article>
            ))}
          </div>
        )}
        {courses.length > 0 && (
          <>
            <h3 className="mt-10 text-lg font-semibold text-gray-900 dark:text-white">Cursos livres e online</h3>
            <ul className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {courses.map((course) => (
                <li key={course.id} className="rounded-xl bg-white p-4 ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
                  <p className="font-medium text-gray-900 dark:text-white">{course.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{courseModalityLabels[course.modality as keyof typeof courseModalityLabels] ?? course.modality}</p>
                  {course.description && <p className="mt-1 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">{course.description}</p>}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
