import Link from 'next/link';
import { withInstitution } from '@/lib/admissions/publicInstitution';
import { formatDateTime } from '@/lib/dates';
import type { AdmissionCall } from '@/types/admissions';

/** Editais com inscricao aberta, cada um com o caminho para se inscrever. */
export default function OpenCallsSection({ calls, slug }: { calls: AdmissionCall[]; slug: string | null }) {
  if (calls.length === 0) return null;
  return (
    <section id="inscricoes" aria-label="Inscrições abertas" className="mx-auto max-w-6xl scroll-mt-6 px-4 py-14">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Inscrições abertas</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {calls.map((call) => (
          <article key={call.id} className="flex flex-col rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
            <h3 className="font-semibold text-gray-900 dark:text-white">{call.title}</h3>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{call.course_name} · {call.offering_name}</p>
            <p className="mt-3 text-sm text-gray-700 dark:text-gray-300">{call.seats} vagas · inscrições até {formatDateTime(call.closes_at)}</p>
            {call.description && <p className="mt-3 line-clamp-3 flex-1 text-sm text-gray-600 dark:text-gray-400">{call.description}</p>}
            <Link href={withInstitution(`/inscricoes/${call.id}`, slug)} className="mt-5 self-start rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700">
              Inscrever-se
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}
