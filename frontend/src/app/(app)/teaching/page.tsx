'use client';

import Link from 'next/link';
import { AcademicCapIcon } from '@heroicons/react/24/outline';
import Spinner from '@/components/common/Spinner';
import { useTeachingOfferings } from '@/lib/hooks/teaching/useTeachingOfferings';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function TeachingPage() {
  const { offerings, loading, error } = useTeachingOfferings();
  useErrorToast(error, 'Erro ao carregar turmas.');

  if (loading && offerings.length === 0) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Diário de classe</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Avaliações, notas, aulas e chamada das suas turmas.</p>
      </div>
      {offerings.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-10 text-center dark:border-gray-600 dark:bg-gray-800">
          <AcademicCapIcon className="mx-auto mb-3 h-12 w-12 text-gray-400" />
          <p className="text-gray-500 dark:text-gray-400">Nenhuma turma sob sua responsabilidade.</p>
        </div>
      ) : (
        <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {offerings.map((offering) => (
            <li key={offering.id}>
              <Link href={`/teaching/offerings/${offering.id}`} className="block rounded-xl border border-gray-200 bg-white p-4 transition-colors hover:border-indigo-400 dark:border-gray-700 dark:bg-gray-800">
                <p className="font-medium text-gray-900 dark:text-white">{offering.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(offering.starts_at).toLocaleDateString('pt-BR')} a {new Date(offering.ends_at).toLocaleDateString('pt-BR')}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
