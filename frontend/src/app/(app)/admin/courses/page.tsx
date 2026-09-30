'use client';

import { useState } from 'react';
import { BookOpenIcon, PencilIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import CourseModal from '@/components/admin/CourseModal';
import CourseDetail from '@/components/admin/courses/CourseDetail';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import CourseCard from '@/components/courses/CourseCard';
import { useCourses } from '@/lib/hooks/admin/useCourses';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';
import type { Course } from '@/types/course';

export default function AdminCoursesPage() {
  const { student } = useAuthStore();
  const canDelete = isAdminRole(student?.role);
  const catalog = useCourses();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [editing, setEditing] = useState<{ course?: Course } | null>(null);
  const [courseToDelete, setCourseToDelete] = useState<Course | null>(null);
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Gerenciar Cursos</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Catálogo, módulos, aulas e pré-requisitos.</p>
        </div>
        {!selectedCourse && (
          <button onClick={() => setEditing({})} className="flex items-center justify-center space-x-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
            <PlusIcon className="w-4 h-4" />
            <span>Novo Curso</span>
          </button>
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
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {catalog.courses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              emptyDescription="Sem descrição cadastrada."
              footer={(
                <>
                  {course.agent_id && <p className="mt-3 truncate text-xs text-gray-500 dark:text-gray-400">Agente: {course.agent_id}</p>}
                  <div className="mt-5 flex flex-wrap items-center gap-2">
                    <button onClick={() => setSelectedId(course.id)} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
                      Gerenciar curso
                    </button>
                    <button onClick={() => setEditing({ course })} aria-label={`Editar ${course.name}`} className="rounded-lg border border-gray-300 p-2 text-gray-500 transition-colors hover:bg-gray-50 hover:text-indigo-600 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    {canDelete && (
                      <button onClick={() => setCourseToDelete(course)} aria-label={`Excluir ${course.name}`} className="rounded-lg border border-gray-300 p-2 text-gray-500 transition-colors hover:bg-red-50 hover:text-red-600 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-red-900/20">
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </>
              )}
            />
          ))}
        </div>
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
