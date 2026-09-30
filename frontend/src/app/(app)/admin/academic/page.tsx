'use client';

import { useState } from 'react';
import { BookOpenIcon, BuildingOffice2Icon, CalendarDaysIcon, ClipboardDocumentListIcon, IdentificationIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import ProgramsSection from '@/components/admin/academic/ProgramsSection';
import ProgramEnrollmentsSection from '@/components/admin/academic/enrollments/ProgramEnrollmentsSection';
import ClassGroupsSection from '@/components/admin/academic/groups/ClassGroupsSection';
import TermsSection from '@/components/admin/academic/terms/TermsSection';
import SubjectsSection from '@/components/admin/academic/SubjectsSection';
import UnitsSection from '@/components/admin/academic/UnitsSection';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { useTerminology } from '@/lib/hooks/useTerminology';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';

type AcademicTab = 'programs' | 'subjects' | 'terms' | 'groups' | 'enrollments' | 'units';

export default function AdminAcademicPage() {
  const terms = useTerminology();
  const canDelete = isAdminRole(useAuthStore((state) => state.student?.role));
  const [tab, setTab] = useState<AcademicTab>('programs');
  const tabs: TabItem<AcademicTab>[] = [
    { id: 'programs', label: terms.programs, icon: ClipboardDocumentListIcon },
    { id: 'subjects', label: terms.subjects, icon: BookOpenIcon },
    { id: 'terms', label: terms.academicTerms, icon: CalendarDaysIcon },
    { id: 'groups', label: 'Turmas', icon: UserGroupIcon },
    { id: 'enrollments', label: 'Matrículas', icon: IdentificationIcon },
    { id: 'units', label: 'Unidades', icon: BuildingOffice2Icon },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Estrutura acadêmica</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Programas, matrizes curriculares, períodos letivos, turmas e matrículas.</p>
      </div>
      <TabNav tabs={tabs} active={tab} onChange={setTab} ariaLabel="Estrutura acadêmica" idPrefix="academic" />
      <div id={`academic-${tab}`} role="tabpanel">
        {tab === 'programs' && <ProgramsSection canDelete={canDelete} />}
        {tab === 'subjects' && <SubjectsSection canDelete={canDelete} />}
        {tab === 'terms' && <TermsSection />}
        {tab === 'groups' && <ClassGroupsSection canDelete={canDelete} />}
        {tab === 'enrollments' && <ProgramEnrollmentsSection />}
        {tab === 'units' && <UnitsSection canDelete={canDelete} />}
      </div>
    </div>
  );
}
