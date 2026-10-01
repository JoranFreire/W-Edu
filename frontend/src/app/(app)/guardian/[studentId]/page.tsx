'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { BanknotesIcon, CalendarDaysIcon, ChartBarIcon, ExclamationTriangleIcon, MegaphoneIcon } from '@heroicons/react/24/outline';
import DependentCharges from '@/components/guardian/DependentCharges';
import DependentNotices from '@/components/guardian/DependentNotices';
import DependentSchoolLife from '@/components/guardian/DependentSchoolLife';
import ReportCardList from '@/components/reportCard/ReportCardList';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { sectionCls } from '@/components/common/formStyles';
import { useDependentOverview } from '@/lib/hooks/guardian/useDependentOverview';
import { useDependents } from '@/lib/hooks/guardian/useDependents';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

type DependentTab = 'report' | 'notices' | 'occurrences' | 'agenda' | 'finance';

export default function DependentPage() {
  const router = useRouter();
  const studentId = Number(useParams<{ studentId: string }>().studentId);
  const { dependents } = useDependents();
  const dependent = dependents.find((item) => item.student.id === studentId);
  const isFinancial = dependent?.is_financial ?? false;
  const { overview, error } = useDependentOverview(studentId, isFinancial);
  const [tab, setTab] = useState<DependentTab>('report');
  useErrorToast(error, 'Erro ao carregar dados do aluno.');

  const tabs: TabItem<DependentTab>[] = [
    { id: 'report', label: 'Boletim', icon: ChartBarIcon },
    { id: 'notices', label: 'Comunicados', icon: MegaphoneIcon, badge: overview?.notices.length },
    { id: 'occurrences', label: 'Ocorrências', icon: ExclamationTriangleIcon },
    { id: 'agenda', label: 'Agenda', icon: CalendarDaysIcon },
    ...(isFinancial ? [{ id: 'finance' as const, label: 'Financeiro', icon: BanknotesIcon }] : []),
  ];

  if (!dependent || !overview) return <Spinner />;
  return (
    <div className="space-y-6">
      <BackButton label="Meus dependentes" onClick={() => router.push('/guardian')} />
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{dependent.student.name}</h1>
      <TabNav tabs={tabs} active={tab} onChange={setTab} ariaLabel="Dados do aluno" idPrefix="dependent" />
      <div id={`dependent-${tab}`} role="tabpanel">
        {tab === 'report' && <ReportCardList entries={overview.reportCard} />}
        {tab === 'notices' && <section className={sectionCls}><DependentNotices notices={overview.notices} /></section>}
        {(tab === 'occurrences' || tab === 'agenda') && <DependentSchoolLife studentId={studentId} view={tab} />}
        {tab === 'finance' && overview.charges && <section className={sectionCls}><DependentCharges charges={overview.charges} /></section>}
      </div>
    </div>
  );
}
