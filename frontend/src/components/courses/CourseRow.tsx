import type { ReactNode } from 'react';
import { AcademicCapIcon } from '@heroicons/react/24/outline';
import { courseModalityLabels } from '@/lib/courses/labels';
import type { Course } from '@/types/course';

const rowCls = 'flex w-full flex-col gap-3 px-4 py-3 text-left sm:flex-row sm:items-center sm:justify-between';

/** Linha de curso (modo lista); com `onClick` a linha inteira vira botao, senao `actions` traz as acoes. */
export default function CourseRow({ course, emptyDescription, onClick, actions }: {
  course: Course;
  emptyDescription: string;
  onClick?: () => void;
  actions?: ReactNode;
}) {
  const content = (
    <>
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-900/20">
          <AcademicCapIcon className="h-5 w-5 text-indigo-600" />
        </div>
        <div className="min-w-0">
          <h3 className="truncate font-medium text-gray-900 dark:text-white">{course.name}</h3>
          <p className="truncate text-sm text-gray-500 dark:text-gray-400">{course.description || emptyDescription}</p>
        </div>
      </div>
      <div className="flex shrink-0 flex-wrap items-center gap-2">
        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
          {courseModalityLabels[course.modality]}
        </span>
        {actions}
      </div>
    </>
  );

  return onClick ? (
    <button type="button" onClick={onClick} className={`${rowCls} transition-colors hover:bg-indigo-50/40 dark:hover:bg-indigo-900/10`}>{content}</button>
  ) : (
    <div className={rowCls}>{content}</div>
  );
}
