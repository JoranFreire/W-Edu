'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { BookOpenIcon, CalendarDaysIcon, ChartBarIcon, ClipboardDocumentListIcon, ExclamationTriangleIcon, GiftIcon, TrophyIcon, UserMinusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import AssessmentPlanPanel from '@/components/teaching/AssessmentPlanPanel';
import DiaryPanel from '@/components/teaching/DiaryPanel';
import GradebookTable from '@/components/teaching/GradebookTable';
import ResultsPanel from '@/components/teaching/ResultsPanel';
import ClassAgendaPanel from '@/components/schoolLife/ClassAgendaPanel';
import ClassOccurrencePanel from '@/components/schoolLife/ClassOccurrencePanel';
import RetentionPanel from '@/components/retention/RetentionPanel';
import OfferingBenefitsPanel from '@/components/social/OfferingBenefitsPanel';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useGradebook } from '@/lib/hooks/teaching/useGradebook';
import { useOfferingPeriods } from '@/lib/hooks/teaching/useOfferingPeriods';
import { useTeachingOffering } from '@/lib/hooks/teaching/useTeachingOffering';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useCurrentRoles } from '@/lib/hooks/useCurrentRoles';

type TeachingTab = 'gradebook' | 'assessments' | 'diary' | 'results' | 'agenda' | 'occurrences' | 'retention' | 'benefits';

const baseTabs: TabItem<TeachingTab>[] = [
  { id: 'gradebook', label: 'Boletim', icon: ChartBarIcon },
  { id: 'assessments', label: 'Avaliações e notas', icon: ClipboardDocumentListIcon },
  { id: 'diary', label: 'Aulas e chamada', icon: BookOpenIcon },
  { id: 'results', label: 'Resultado', icon: TrophyIcon },
];
const agendaTab: TabItem<TeachingTab> = { id: 'agenda', label: 'Agenda', icon: CalendarDaysIcon };
const occurrencesTab: TabItem<TeachingTab> = { id: 'occurrences', label: 'Ocorrências', icon: ExclamationTriangleIcon };
const socialTabs: TabItem<TeachingTab>[] = [
  { id: 'retention', label: 'Frequência e evasão', icon: UserMinusIcon },
  { id: 'benefits', label: 'Benefícios', icon: GiftIcon },
];

export default function TeachingOfferingPage() {
  const router = useRouter();
  const offeringId = useParams<{ offeringId: string }>().offeringId;
  const { isAdmin, has } = useCurrentRoles();
  const isCoordination = isAdmin || has('coordinator');
  const { offering, error, syncGroup } = useTeachingOffering(offeringId);
  const { periods } = useOfferingPeriods(offering?.term_id);
  const { gradebook, reload } = useGradebook(offeringId);
  const [tab, setTab] = useState<TeachingTab>('gradebook');
  useErrorToast(error, 'Turma não encontrada ou sem acesso.');

  const handleSync = async () => {
    try {
      const created = await syncGroup();
      toast.success(`${created} aluno(s) inscrito(s) a partir da turma-grupo.`);
      reload();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao sincronizar alunos.'));
    }
  };

  if (!offering) return <Spinner />;
  // A agenda pertence a turma-grupo: so aparece quando a oferta esta ligada a uma.
  const tabs = [...baseTabs, ...(offering.class_group_id ? [agendaTab] : []), occurrencesTab, ...socialTabs];
  const students = gradebook?.rows.map((row) => row.student) ?? [];
  return (
    <div className="space-y-6">
      <BackButton label="Minhas turmas" onClick={() => router.push('/teaching')} />
      <div className="flex flex-wrap items-start justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{offering.name}</h1>
        {isCoordination && offering.class_group_id && (
          <button onClick={handleSync} className={secondaryButtonCls}>Sincronizar alunos da turma-grupo</button>
        )}
      </div>
      <TabNav tabs={tabs} active={tab} onChange={setTab} ariaLabel="Diário da turma" idPrefix="teaching" />
      <div id={`teaching-${tab}`} role="tabpanel">
        {tab === 'gradebook' && (
          <section className={sectionCls}>{gradebook ? <GradebookTable gradebook={gradebook} /> : <Spinner variant="panel" />}</section>
        )}
        {tab === 'assessments' && <AssessmentPlanPanel offeringId={offeringId} periods={periods} onGradesChanged={reload} />}
        {tab === 'diary' && <DiaryPanel offeringId={offeringId} onAttendanceChanged={reload} />}
        {tab === 'results' && <ResultsPanel offeringId={offeringId} periods={periods} isCoordination={isCoordination} onChanged={reload} />}
        {tab === 'agenda' && offering.class_group_id && <ClassAgendaPanel groupId={offering.class_group_id} offeringId={offeringId} />}
        {tab === 'occurrences' && <ClassOccurrencePanel students={students} classGroupId={offering.class_group_id} />}
        {tab === 'retention' && <RetentionPanel offeringId={offeringId} canReadmit={isCoordination} />}
        {tab === 'benefits' && <OfferingBenefitsPanel offeringId={offeringId} />}
      </div>
    </div>
  );
}
