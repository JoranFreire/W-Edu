'use client';

import { BookOpenIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import CollectionView from '@/components/common/CollectionView';
import Spinner from '@/components/common/Spinner';
import ViewModeToggle from '@/components/common/ViewModeToggle';
import CatalogCourseActions from '@/components/courses/catalog/CatalogCourseActions';
import LearningPathsSection from '@/components/courses/catalog/LearningPathsSection';
import CourseCard from '@/components/courses/CourseCard';
import CourseRow from '@/components/courses/CourseRow';
import { useCourseCatalog } from '@/lib/hooks/courses/useCourseCatalog';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useViewMode } from '@/lib/hooks/useViewMode';
import { useAuthStore } from '@/store/authStore';
import type { Course } from '@/types/course';

const EMPTY_DESCRIPTION = 'Sem descrição.';

export default function CoursesPage() {
  const { student } = useAuthStore();
  const catalog = useCourseCatalog(student?.id);
  const [viewMode, setViewMode] = useViewMode('courses');
  useErrorToast(catalog.error, 'Erro ao carregar cursos.');

  const enroll = async (courseId: number) => {
    try {
      await catalog.enroll(courseId);
      toast.success('Matriculado com sucesso!');
    } catch {
      toast.error('Erro ao matricular no curso.');
    }
  };

  if (catalog.loading && catalog.courses.length === 0) return <Spinner />;

  const actionsFor = (course: Course) => (
    <CatalogCourseActions courseId={course.id} enrolled={catalog.isEnrolled(course.id)} onEnroll={() => enroll(course.id)} />
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Catálogo de Cursos</h1>
        {catalog.courses.length > 0 && <ViewModeToggle mode={viewMode} onChange={setViewMode} />}
      </div>

      {catalog.learningPaths.length > 0 && (
        <LearningPathsSection
          paths={catalog.learningPaths}
          pathCourses={catalog.pathCourses}
          isEnrolled={catalog.isEnrolled}
          courseName={catalog.courseName}
          onEnroll={enroll}
        />
      )}

      {catalog.courses.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-10 text-center dark:border-gray-600 dark:bg-gray-800">
          <BookOpenIcon className="mx-auto mb-3 h-12 w-12 text-gray-400" />
          <p className="text-gray-500 dark:text-gray-400">Nenhum curso disponível no momento.</p>
        </div>
      ) : (
        <CollectionView
          mode={viewMode}
          items={catalog.courses}
          itemKey={(course) => course.id}
          label="Cursos"
          renderCard={(course) => (
            <CourseCard course={course} emptyDescription={EMPTY_DESCRIPTION} footer={<div className="mt-4">{actionsFor(course)}</div>} />
          )}
          renderRow={(course) => <CourseRow course={course} emptyDescription={EMPTY_DESCRIPTION} actions={actionsFor(course)} />}
        />
      )}
    </div>
  );
}
