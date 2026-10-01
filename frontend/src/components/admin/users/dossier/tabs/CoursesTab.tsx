import { EmptyPanel, PanelTitle, listCls, rowCls } from '@/components/admin/users/dossier/DossierParts';
import type { DossierCourse } from '@/types/userDossier';

function CourseRows({ courses }: { courses: DossierCourse[] }) {
  return (
    <ul className={listCls}>
      {courses.map((course) => (
        <li key={course.course_id} className={rowCls}>
          <div className="min-w-0">
            <p className="font-medium text-gray-900 dark:text-white">{course.course_name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {course.done_lessons}/{course.total_lessons} aulas
              {course.last_activity_at ? ` · última atividade em ${new Date(course.last_activity_at).toLocaleDateString('pt-BR')}` : ''}
            </p>
          </div>
          <div className="flex w-full items-center gap-2 sm:w-48">
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700" role="progressbar" aria-valuenow={course.progress_percent} aria-valuemin={0} aria-valuemax={100} aria-label={`Progresso em ${course.course_name}`}>
              <div className={`h-full ${course.completed ? 'bg-emerald-500' : 'bg-indigo-500'}`} style={{ width: `${course.progress_percent}%` }} />
            </div>
            <span className="w-10 text-right text-xs text-gray-500 dark:text-gray-400">{course.progress_percent}%</span>
          </div>
        </li>
      ))}
    </ul>
  );
}

/** Cursos em andamento e concluidos, com o progresso nas aulas. */
export default function CoursesTab({ courses }: { courses: DossierCourse[] }) {
  if (courses.length === 0) return <EmptyPanel>Nenhum curso.</EmptyPanel>;
  const completed = courses.filter((course) => course.completed);
  const ongoing = courses.filter((course) => !course.completed);
  return (
    <div className="space-y-6">
      {ongoing.length > 0 && <div><PanelTitle>Em andamento ({ongoing.length})</PanelTitle><CourseRows courses={ongoing} /></div>}
      {completed.length > 0 && <div><PanelTitle>Concluídos ({completed.length})</PanelTitle><CourseRows courses={completed} /></div>}
    </div>
  );
}
