'use client';

import { type ReactNode, useState } from 'react';
import {
  AcademicCapIcon, ArchiveBoxIcon, BanknotesIcon, BookOpenIcon, ExclamationTriangleIcon, GiftIcon, ShieldCheckIcon,
  Squares2X2Icon, UserGroupIcon, UsersIcon,
} from '@heroicons/react/24/outline';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import AcademicTab from '@/components/admin/users/dossier/tabs/AcademicTab';
import BenefitsTab from '@/components/admin/users/dossier/tabs/BenefitsTab';
import CertificatesTab from '@/components/admin/users/dossier/tabs/CertificatesTab';
import CoursesTab from '@/components/admin/users/dossier/tabs/CoursesTab';
import FamilyTab from '@/components/admin/users/dossier/tabs/FamilyTab';
import FinanceTab from '@/components/admin/users/dossier/tabs/FinanceTab';
import MaterialsTab from '@/components/admin/users/dossier/tabs/MaterialsTab';
import OccurrencesTab from '@/components/admin/users/dossier/tabs/OccurrencesTab';
import SummaryTab from '@/components/admin/users/dossier/tabs/SummaryTab';
import { type DossierTab, dossierTabs } from '@/lib/users/dossierTabs';
import type { UserDossier } from '@/types/userDossier';

const ICONS: Record<DossierTab, TabItem<DossierTab>['icon']> = {
  summary: Squares2X2Icon, family: UserGroupIcon, dependents: UsersIcon, academic: AcademicCapIcon, courses: BookOpenIcon, certificates: ShieldCheckIcon,
  benefits: GiftIcon, materials: ArchiveBoxIcon, finance: BanknotesIcon, occurrences: ExclamationTriangleIcon,
};

/** Abas do dossie dentro do cartao, abaixo do cabecalho; o Resumo traz a propria lateral, as demais tem recuo. */
export default function DossierTabs({ dossier, permissions }: { dossier: UserDossier; permissions: string[] }) {
  const specs = dossierTabs(dossier);
  const [chosen, setChosen] = useState<DossierTab>('summary');
  const active = specs.some((spec) => spec.id === chosen) ? chosen : 'summary';
  const tabs: TabItem<DossierTab>[] = specs.map((spec) => ({ ...spec, icon: ICONS[spec.id] }));

  const panels: Record<DossierTab, () => ReactNode> = {
    summary: () => <SummaryTab dossier={dossier} />,
    family: () => <FamilyTab links={dossier.guardians ?? []} emptyText="Nenhum responsável vinculado. Vincule pela ficha do aluno na Secretaria." />,
    dependents: () => <FamilyTab links={dossier.dependents ?? []} emptyText="Nenhum dependente vinculado." />,
    academic: () => <AcademicTab dossier={dossier} canOpenRecord={permissions.includes('secretariat.access')} canOpenDiary={permissions.includes('teaching.access')} />,
    courses: () => <CoursesTab courses={dossier.courses} />,
    certificates: () => <CertificatesTab certificates={dossier.certificates} />,
    benefits: () => <BenefitsTab benefits={dossier.benefits ?? []} />,
    materials: () => <MaterialsTab requests={dossier.materials ?? []} />,
    finance: () => (dossier.finance ? <FinanceTab finance={dossier.finance} /> : null),
    occurrences: () => (dossier.occurrences ? <OccurrencesTab occurrences={dossier.occurrences} /> : null),
  };

  return (
    <>
      <div className="px-5 sm:px-6">
        <TabNav tabs={tabs} active={active} onChange={setChosen} ariaLabel="Dossiê" idPrefix="dossier" />
      </div>
      <div id={`dossier-${active}`} role="tabpanel" className={active === 'summary' ? '' : 'p-5 sm:p-6'}>
        {panels[active]()}
      </div>
    </>
  );
}
