'use client';

import { useState } from 'react';
import { AcademicCapIcon } from '@heroicons/react/24/outline';
import CourseCertificationPanel from '@/components/admin/certificates/CourseCertificationPanel';
import BackButton from '@/components/common/BackButton';
import CollectionView from '@/components/common/CollectionView';
import Spinner from '@/components/common/Spinner';
import ViewModeToggle from '@/components/common/ViewModeToggle';
import CourseCard from '@/components/courses/CourseCard';
import CourseRow from '@/components/courses/CourseRow';
import { useCertificateCatalog } from '@/lib/hooks/admin/useCertificateCatalog';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useViewMode } from '@/lib/hooks/useViewMode';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';
import type { Course } from '@/types/course';

const CERTIFICATE_HINT = 'Gerencie regras, emissão e validação dos certificados deste curso.';

export default function AdminCertificatesPage() {
  const { student } = useAuthStore();
  const catalog = useCertificateCatalog();
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [viewMode, setViewMode] = useViewMode('admin-certificates');
  useErrorToast(catalog.error, 'Erro ao carregar cursos.');

  if (catalog.loading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Certificados</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Regras de aprovação, emissão e validação pública.</p>
      </div>

      {!selectedCourse ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <AcademicCapIcon className="w-5 h-5 text-indigo-600" />
              <h2 className="font-semibold text-gray-900 dark:text-white">Selecione um curso</h2>
            </div>
            {catalog.courses.length > 0 && <ViewModeToggle mode={viewMode} onChange={setViewMode} />}
          </div>
          {catalog.courses.length === 0 ? (
            <div className="rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">
              Nenhum curso cadastrado.
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
                  emptyDescription={CERTIFICATE_HINT}
                  onClick={() => setSelectedCourse(course)}
                  footer={<span className="mt-4 inline-flex text-sm font-medium text-indigo-600 dark:text-indigo-400">Gerenciar certificados</span>}
                />
              )}
              renderRow={(course) => (
                <CourseRow
                  course={course}
                  emptyDescription={CERTIFICATE_HINT}
                  onClick={() => setSelectedCourse(course)}
                  actions={<span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">Gerenciar certificados</span>}
                />
              )}
            />
          )}
        </div>
      ) : (
        <>
          <div className="space-y-5">
            <BackButton label="Voltar para cursos" onClick={() => setSelectedCourse(null)} />
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{selectedCourse.name}</h2>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Configure e acompanhe certificados deste curso.</p>
            </div>
          </div>
          <CourseCertificationPanel key={selectedCourse.id} courseId={selectedCourse.id} students={catalog.students} canRevoke={isAdminRole(student?.role)} />
        </>
      )}
    </div>
  );
}
