import type { ReactNode } from 'react';
import { AcademicCapIcon } from '@heroicons/react/24/outline';
import { courseModalityLabels } from '@/lib/courses/labels';
import type { Course } from '@/types/course';

const cardCls = 'group rounded-xl border border-gray-200 bg-white p-5 text-left transition-colors hover:border-indigo-300 hover:bg-indigo-50/40 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-indigo-700 dark:hover:bg-indigo-900/10';

/** Cartao de curso; com `onClick` o cartao inteiro vira botao, senao `footer` traz as acoes. */
export default function CourseCard({ course, emptyDescription, onClick, footer }: {
  course: Course;
  emptyDescription: string;
  onClick?: () => void;
  footer?: ReactNode;
}) {
  const content = (
    <>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-900/20">
          <AcademicCapIcon className="h-5 w-5 text-indigo-600" />
        </div>
        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
          {courseModalityLabels[course.modality]}
        </span>
      </div>
      <h3 className="line-clamp-2 font-semibold text-gray-900 group-hover:text-indigo-700 dark:text-white dark:group-hover:text-indigo-300">{course.name}</h3>
      <p className="mt-2 line-clamp-2 min-h-10 text-sm text-gray-500 dark:text-gray-400">{course.description || emptyDescription}</p>
      {footer}
    </>
  );

  return onClick ? (
    <button type="button" onClick={onClick} className={cardCls}>{content}</button>
  ) : (
    <div className={cardCls}>{content}</div>
  );
}
