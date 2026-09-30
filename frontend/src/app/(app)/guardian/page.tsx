'use client';

import Link from 'next/link';
import { UserIcon } from '@heroicons/react/24/outline';
import Spinner from '@/components/common/Spinner';
import { relationshipLabels } from '@/lib/academic/guardianLabels';
import { useDependents } from '@/lib/hooks/guardian/useDependents';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function GuardianHomePage() {
  const { dependents, loading, error } = useDependents();
  useErrorToast(error, 'Erro ao carregar dependentes.');

  if (loading && dependents.length === 0) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Meus dependentes</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Boletim, comunicados e financeiro de cada aluno.</p>
      </div>
      {dependents.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno vinculado. Procure a secretaria da escola.</p>
      ) : (
        <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {dependents.map((dependent) => (
            <li key={dependent.link_id}>
              <Link href={`/guardian/${dependent.student.id}`} className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 transition-colors hover:border-indigo-400 dark:border-gray-700 dark:bg-gray-800">
                <UserIcon className="h-8 w-8 rounded-full bg-indigo-50 p-1.5 text-indigo-600 dark:bg-indigo-900/30" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{dependent.student.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{relationshipLabels[dependent.relationship_kind]}{dependent.is_financial ? ' · responsável financeiro' : ''}</p>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
