'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import PublicShell from '@/components/admissions/PublicShell';
import { callStatusLabels } from '@/lib/academic/admissionLabels';
import { withInstitution } from '@/lib/admissions/publicInstitution';
import { formatDateTime } from '@/lib/dates';
import { usePublicCalls } from '@/lib/hooks/admissions/usePublicCalls';

function Catalog() {
  const institution = useSearchParams().get('institution');
  const { calls, loading, error } = usePublicCalls(institution);
  if (error) return <p className="text-sm text-red-600 dark:text-red-400">Instituição não encontrada.</p>;
  if (loading) return <p className="text-sm text-gray-500 dark:text-gray-400">Carregando...</p>;
  if (calls.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum edital publicado no momento.</p>;
  return (
    <ul className="space-y-3">
      {calls.map((call) => (
        <li key={call.id}>
          <Link href={withInstitution(`/inscricoes/${call.id}`, institution)} className="block rounded-xl border border-gray-200 bg-white p-5 transition-colors hover:border-indigo-400 dark:border-gray-700 dark:bg-gray-800">
            <p className="font-semibold text-gray-900 dark:text-white">{call.title}</p>
            <p className="text-sm text-gray-600 dark:text-gray-300">{call.course_name} · {call.seats} vagas · gratuito</p>
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {call.is_accepting ? `Inscrições até ${formatDateTime(call.closes_at)}` : callStatusLabels[call.status]}
            </p>
          </Link>
        </li>
      ))}
    </ul>
  );
}

/** Catalogo publico de editais da instituicao (subdominio ou ?institution=). */
export default function PublicCallsPage() {
  return (
    <PublicShell>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Cursos com inscrições</h1>
      <Suspense fallback={null}><Catalog /></Suspense>
    </PublicShell>
  );
}
