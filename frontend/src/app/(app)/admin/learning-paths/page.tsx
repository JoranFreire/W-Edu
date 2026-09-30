'use client';

import { useState } from 'react';
import { AcademicCapIcon, PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import LearningPathCard from '@/components/admin/LearningPathCard';
import LearningPathModal from '@/components/admin/LearningPathModal';
import AddPathCourseModal from '@/components/admin/learning-paths/AddPathCourseModal';
import Spinner from '@/components/common/Spinner';
import { apiErrorMessage } from '@/lib/api/errors';
import { type LearningPathInput, useLearningPaths } from '@/lib/hooks/admin/useLearningPaths';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';
import type { LearningPath } from '@/types/course';

export default function AdminLearningPathsPage() {
  const { student } = useAuthStore();
  const canDelete = isAdminRole(student?.role);
  const paths = useLearningPaths();
  const [editing, setEditing] = useState<{ path?: LearningPath } | null>(null);
  const [addingToPathId, setAddingToPathId] = useState<number | null>(null);
  const [pathToDelete, setPathToDelete] = useState<LearningPath | null>(null);
  const [courseToRemove, setCourseToRemove] = useState<{ pathId: number; courseId: number } | null>(null);

  useErrorToast(paths.error, 'Erro ao carregar trilhas.');

  const availableCourses = (pathId: number) => {
    const linkedIds = new Set((paths.pathCourses[pathId] ?? []).map((item) => item.course_id));
    return paths.courses.filter((course) => !linkedIds.has(course.id));
  };

  const savePath = async (input: LearningPathInput) => {
    try {
      await paths.savePath(editing?.path?.id ?? null, input);
      toast.success(editing?.path ? 'Trilha atualizada.' : 'Trilha criada.');
      setEditing(null);
    } catch { toast.error('Erro ao salvar trilha.'); }
  };

  const deletePath = async () => {
    if (!pathToDelete) return;
    try {
      await paths.deletePath(pathToDelete.id);
      toast.success('Trilha excluída.');
      setPathToDelete(null);
    } catch { toast.error('Erro ao excluir trilha.'); }
  };

  const openAddCourse = (pathId: number) => {
    if (!availableCourses(pathId).length) { toast.error('Não há cursos disponíveis para adicionar.'); return; }
    setAddingToPathId(pathId);
  };

  const addCourse = async (courseId: number) => {
    if (!addingToPathId) return;
    try {
      await paths.addCourse(addingToPathId, courseId);
      toast.success('Curso adicionado.');
      setAddingToPathId(null);
    } catch (error) { toast.error(apiErrorMessage(error, 'Erro ao adicionar curso.')); }
  };

  const removeCourse = async () => {
    if (!courseToRemove) return;
    try {
      await paths.removeCourse(courseToRemove.pathId, courseToRemove.courseId);
      toast.success('Curso removido.');
      setCourseToRemove(null);
    } catch { toast.error('Erro ao remover curso.'); }
  };

  if (paths.loading && paths.paths.length === 0) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Trilhas</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Sequências de cursos para jornadas de aprendizagem.</p>
        </div>
        <button onClick={() => setEditing({})} className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
          <PlusIcon className="h-4 w-4" /><span>Nova trilha</span>
        </button>
      </div>

      {paths.paths.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-10 text-center dark:border-gray-600 dark:bg-gray-800">
          <AcademicCapIcon className="mx-auto mb-3 h-12 w-12 text-gray-400" />
          <p className="text-gray-500 dark:text-gray-400">Nenhuma trilha criada.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {paths.paths.map((path) => (
            <LearningPathCard key={path.id} path={path} courses={paths.courses} pathCourses={paths.pathCourses[path.id] ?? []}
              canDelete={canDelete} onEdit={(p) => setEditing({ path: p })} onDelete={() => setPathToDelete(path)}
              onAddCourse={openAddCourse} onRemoveCourse={(pathId, courseId) => setCourseToRemove({ pathId, courseId })} />
          ))}
        </div>
      )}

      {editing && <LearningPathModal path={editing.path} onClose={() => setEditing(null)} onSave={savePath} />}
      {pathToDelete && (
        <ConfirmDialog
          title="Excluir trilha"
          message={`Deseja excluir "${pathToDelete.name}"?`}
          confirmLabel="Excluir"
          danger
          onCancel={() => setPathToDelete(null)}
          onConfirm={deletePath}
        />
      )}
      {courseToRemove && (
        <ConfirmDialog
          title="Remover curso"
          message="Este curso será removido da trilha."
          confirmLabel="Remover"
          danger
          onCancel={() => setCourseToRemove(null)}
          onConfirm={removeCourse}
        />
      )}
      {addingToPathId && (
        <AddPathCourseModal availableCourses={availableCourses(addingToPathId)} onAdd={addCourse} onClose={() => setAddingToPathId(null)} />
      )}
    </div>
  );
}
