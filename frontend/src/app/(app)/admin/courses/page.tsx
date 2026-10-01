'use client';

import { useState } from 'react';
import { BookOpenIcon, PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import CourseModal from '@/components/admin/CourseModal';
import CourseCatalogActions from '@/components/admin/courses/CourseCatalogActions';
import CourseDetail from '@/components/admin/courses/CourseDetail';
import BackButton from '@/components/common/BackButton';
import CollectionView from '@/components/common/CollectionView';
import Spinner from '@/components/common/Spinner';
import ViewModeToggle from '@/components/common/ViewModeToggle';
import CourseCard from '@/components/courses/CourseCard';
import CourseRow from '@/components/courses/CourseRow';
import { useCourses } from '@/lib/hooks/admin/useCourses';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useViewMode } from '@/lib/hooks/useViewMode';
import type { Course } from '@/types/course';
import { useCurrentRoles } from '@/lib/hooks/useCurrentRoles';

export default function AdminCoursesPage() {
  const canDelete = useCurrentRoles().isAdmin;
  const catalog = useCourses();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editing, setEditing] = useState<{ course?: Course } | null>(null);
  const [courseToDelete, setCourseToDelete] = useState<Course | null>(null);
  const [viewMode, setViewMode] = useViewMode('admin-courses');
  useErrorToast(catalog.error, 'Erro ao carregar cursos.');

  // O curso aberto vem sempre da lista atual, para refletir edicoes.
  const selectedCourse = catalog.courses.find((course) => course.id === selectedId) ?? null;

  const saveCourse = async (input: Partial<Course>) => {
    try {
      await catalog.save(editing?.course?.id ?? null, input);
      toast.success(editing?.course ? 'Curso atualizado!' : 'Curso criado!');
      setEditing(null);
    } catch { toast.error('Erro ao salvar curso.'); }
  };

  const deleteCourse = async () => {
    if (!courseToDelete) return;
    try {
      await catalog.remove(courseToDelete.id);
      toast.success('Curso excluído.');
      if (selectedId === courseToDelete.id) setSelectedId(null);
      setCourseToDelete(null);
    } catch { toast.error('Erro ao excluir curso.'); }
  };

  if (catalog.loading && catalog.courses.length === 0) return <Spinner />;

  const actionsFor = (course: Course) => (
    <CourseCatalogActions
      course={course}
      canDelete={canDelete}
      onManage={() => setSelectedId(course.id)}
      onEdit={() => setEditing({ course })}
      onDelete={() => setCourseToDelete(course)}
    />
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Gerenciar Cursos</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Catálogo, módulos, aulas e pré-requisitos.</p>
        </div>
        {!selectedCourse && (
          <div className="flex items-center gap-3">
            {catalog.courses.length > 0 && <ViewModeToggle mode={viewMode} onChange={setViewMode} />}
            <button onClick={() => setEditing({})} className="flex flex-1 items-center justify-center space-x-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 sm:flex-none">
              <PlusIcon className="w-4 h-4" />
              <span>Novo Curso</span>
            </button>
          </div>
        )}
      </div>

      {selectedCourse ? (
        <div className="space-y-5">
          <BackButton label="Voltar para cursos" onClick={() => setSelectedId(null)} />
          <CourseDetail key={selectedCourse.id} course={selectedCourse} courses={catalog.courses} canDelete={canDelete} onEdit={() => setEditing({ course: selectedCourse })} />
        </div>
      ) : catalog.courses.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-300 dark:border-gray-600 p-10 text-center">
          <BookOpenIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400">Nenhum curso criado ainda.</p>
        </div>
      ) : (
        <CollectionView
          mode={viewMode}
          items={catalog.courses}
          itemKey={(course) => course.id}
          label="Cursos"
          renderCard={(course) => (
            <CourseCard
              course={course}
              emptyDescription="Sem descrição cadastrada."
              footer={(
                <>
                  {course.agent_id && <p className="mt-3 truncate text-xs text-gray-500 dark:text-gray-400">Agente: {course.agent_id}</p>}
                  <div className="mt-5">{actionsFor(course)}</div>
                </>
              )}
            />
          )}
          renderRow={(course) => <CourseRow course={course} emptyDescription="Sem descrição cadastrada." actions={actionsFor(course)} />}
        />
      )}

      {editing && <CourseModal course={editing.course} onClose={() => setEditing(null)} onSave={saveCourse} />}
      {courseToDelete && (
        <ConfirmDialog
          title="Excluir curso"
          message={`Deseja excluir "${courseToDelete.name}"?`}
          confirmLabel="Excluir"
          danger
          onCancel={() => setCourseToDelete(null)}
          onConfirm={deleteCourse}
        />
      )}
    </div>
  );
}
