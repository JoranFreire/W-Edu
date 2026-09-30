import { Suspense } from 'react';
import Link from 'next/link';
import { DocumentCheckIcon } from '@heroicons/react/24/outline';
import DeclarationValidator from '@/components/secretariat/DeclarationValidator';

export default function ValidateDeclarationPage() {
  return (
    <main className="min-h-screen bg-gray-50 px-4 py-10 dark:bg-gray-900">
      <div className="mx-auto max-w-xl">
        <Link href="/login" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">Entrar na plataforma</Link>
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
              <DocumentCheckIcon className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">Validar declaração</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Informe o código impresso na declaração acadêmica.</p>
            </div>
          </div>
          <Suspense fallback={null}>
            <DeclarationValidator />
          </Suspense>
        </div>
      </div>
    </main>
  );
}
