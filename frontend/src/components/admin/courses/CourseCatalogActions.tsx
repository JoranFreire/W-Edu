import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import type { Course } from '@/types/course';

/** Acoes de um curso no catalogo do admin: gerenciar, editar e excluir. */
export default function CourseCatalogActions({ course, canDelete, onManage, onEdit, onDelete }: {
  course: Course;
  canDelete: boolean;
  onManage: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <button onClick={onManage} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
        Gerenciar curso
      </button>
      <button onClick={onEdit} aria-label={`Editar ${course.name}`} className="rounded-lg border border-gray-300 p-2 text-gray-500 transition-colors hover:bg-gray-50 hover:text-indigo-600 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
        <PencilIcon className="h-4 w-4" />
      </button>
      {canDelete && (
        <button onClick={onDelete} aria-label={`Excluir ${course.name}`} className="rounded-lg border border-gray-300 p-2 text-gray-500 transition-colors hover:bg-red-50 hover:text-red-600 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-red-900/20">
          <TrashIcon className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
