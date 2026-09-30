'use client';

import { useState } from 'react';
import { BookOpenIcon, ListBulletIcon, PencilIcon, QueueListIcon } from '@heroicons/react/24/outline';
import LessonsPanel from '@/components/admin/LessonsPanel';
import ModulesPanel from '@/components/admin/ModulesPanel';
import PrerequisitesPanel from '@/components/admin/PrerequisitesPanel';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { courseModalityLabels } from '@/lib/courses/labels';
import { useCourseContent } from '@/lib/hooks/admin/useCourseContent';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Course } from '@/types/course';

type CourseTab = 'modules' | 'lessons' | 'prerequisites';

/** Cabecalho do curso e abas de modulos, aulas e pre-requisitos. */
export default function CourseDetail({ course, courses, canDelete, onEdit }: {
  course: Course;
  courses: Course[];
  canDelete: boolean;
  onEdit: () => void;
}) {
  const content = useCourseContent(course.id);
  const [activeTab, setActiveTab] = useState<CourseTab>('modules');
  useErrorToast(content.error, 'Erro ao carregar detalhes do curso.');

  const tabs: TabItem<CourseTab>[] = [
    { id: 'modules', label: 'Módulos', icon: QueueListIcon, badge: content.modules.length },
    { id: 'lessons', label: 'Aulas', icon: BookOpenIcon, badge: content.lessons.length },
    { id: 'prerequisites', label: 'Pré-requisitos', icon: ListBulletIcon, badge: content.prerequisites.length },
  ];
  const firstLoad = content.loading && !content.modules.length && !content.lessons.length && !content.prerequisites.length;

  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{course.name}</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {courseModalityLabels[course.modality]}{course.agent_id ? ` · Agente: ${course.agent_id}` : ''}
          </p>
          {course.description && <p className="mt-2 max-w-3xl text-sm text-gray-600 dark:text-gray-300">{course.description}</p>}
        </div>
        <button onClick={onEdit} className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
          <PencilIcon className="h-4 w-4" />
          <span>Editar curso</span>
        </button>
      </div>

      <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Gestão do curso" idPrefix="course" />

      {firstLoad ? (
        <Spinner variant="panel" />
      ) : (
        <div id={`course-${activeTab}`} role="tabpanel" className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
          {activeTab === 'modules' && <ModulesPanel courseId={course.id} modules={content.modules} canDelete={canDelete} onChanged={content.reloadModules} />}
          {activeTab === 'lessons' && <LessonsPanel courseId={course.id} lessons={content.lessons} modules={content.modules} canDelete={canDelete} onChanged={content.reloadLessons} />}
          {activeTab === 'prerequisites' && <PrerequisitesPanel courseId={course.id} courses={courses} prerequisites={content.prerequisites} canDelete={canDelete} onChanged={content.reloadPrerequisites} />}
        </div>
      )}
    </>
  );
}
