import Link from 'next/link';
import { BookOpenIcon } from '@heroicons/react/24/outline';
import type { Course } from '@/types/course';

export default function EnrolledCoursesGrid({ courses }: { courses: Course[] }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Meus Cursos</h2>
        <Link href="/courses" className="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 font-medium">Ver todos</Link>
      </div>
      {courses.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-300 dark:border-gray-600 p-10 text-center">
          <BookOpenIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400">Você ainda não está matriculado em nenhum curso.</p>
          <Link href="/courses" className="mt-3 inline-block text-sm font-medium text-indigo-600 hover:underline">Explorar cursos</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course) => (
            <Link key={course.id} href={`/courses/${course.id}`}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center mb-3">
                <BookOpenIcon className="w-5 h-5 text-indigo-600" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white">{course.name}</h3>
              {course.description && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{course.description}</p>}
              <span className="mt-3 inline-block text-xs font-medium text-indigo-600 dark:text-indigo-400">Continuar →</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
