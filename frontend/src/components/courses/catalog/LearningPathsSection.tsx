import Link from 'next/link';
import type { LearningPath, LearningPathCourse } from '@/types/course';

/** Trilhas de aprendizagem com a sequencia de cursos e a situacao do aluno em cada um. */
export default function LearningPathsSection({ paths, pathCourses, isEnrolled, courseName, onEnroll }: {
  paths: LearningPath[];
  pathCourses: Record<string, LearningPathCourse[]>;
  isEnrolled: (courseId: string) => boolean;
  courseName: (courseId: string) => string;
  onEnroll: (courseId: string) => void;
}) {
  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Trilhas de aprendizagem</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Jornadas organizadas por sequência de cursos.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {paths.map((path) => {
          const items = pathCourses[path.id] ?? [];
          return (
            <div key={path.id} className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
              <h3 className="font-semibold text-gray-900 dark:text-white">{path.name}</h3>
              {path.description && <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{path.description}</p>}
              {items.length === 0 ? (
                <p className="mt-3 text-sm text-gray-400">Nenhum curso vinculado.</p>
              ) : (
                <div className="mt-4 space-y-2">
                  {items.map((item) => {
                    const enrolled = isEnrolled(item.course_id);
                    return (
                      <div key={item.id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-900">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-gray-900 dark:text-white">{item.order}. {courseName(item.course_id)}</p>
                          {enrolled && <p className="text-xs text-green-600 dark:text-green-400">Matriculado</p>}
                        </div>
                        {enrolled ? (
                          <Link href={`/courses/${item.course_id}`} className="text-xs font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">
                            Continuar
                          </Link>
                        ) : (
                          <button onClick={() => onEnroll(item.course_id)} className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700">
                            Matricular
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
