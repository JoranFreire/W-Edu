import type { ReactNode } from 'react';
import Link from 'next/link';

/** Moldura das paginas publicas de inscricao (sem menu da plataforma). */
export default function PublicShell({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen bg-gray-50 px-4 py-10 dark:bg-gray-900">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center justify-between">
          <Link href="/inscricoes" className="text-sm font-semibold text-gray-900 dark:text-white">Inscrições em cursos</Link>
          <Link href="/login" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">Entrar</Link>
        </div>
        {children}
      </div>
    </main>
  );
}
