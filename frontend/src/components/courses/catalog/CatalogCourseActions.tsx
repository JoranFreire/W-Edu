import Link from 'next/link';
import { PlusCircleIcon } from '@heroicons/react/24/outline';

/** Acao do aluno sobre um curso do catalogo: continuar (matriculado) ou matricular. */
export default function CatalogCourseActions({ courseId, enrolled, onEnroll }: {
  courseId: string;
  enrolled: boolean;
  onEnroll: () => void;
}) {
  if (enrolled) {
    return (
      <div className="flex items-center gap-3">
        <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
          Matriculado
        </span>
        <Link href={`/courses/${courseId}`} className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">
          Continuar →
        </Link>
      </div>
    );
  }
  return (
    <button
      onClick={onEnroll}
      className="flex items-center space-x-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
    >
      <PlusCircleIcon className="h-4 w-4" />
      <span>Matricular</span>
    </button>
  );
}
