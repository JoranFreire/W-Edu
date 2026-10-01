'use client';

import { useState } from 'react';
import { BriefcaseIcon, ChartPieIcon, DocumentTextIcon, SparklesIcon } from '@heroicons/react/24/outline';
import FinalProjectCard from '@/components/completion/FinalProjectCard';
import IntegralizationSummary from '@/components/completion/IntegralizationSummary';
import InternshipCard from '@/components/completion/InternshipCard';
import InternshipLogs from '@/components/completion/InternshipLogs';
import MyActivitiesSection from '@/components/completion/MyActivitiesSection';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { sectionCls } from '@/components/common/formStyles';
import { useMyCompletion } from '@/lib/hooks/completion/useMyCompletion';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

type CompletionTab = 'requirements' | 'activities' | 'internships' | 'final';

const tabs: TabItem<CompletionTab>[] = [
  { id: 'requirements', label: 'Requisitos', icon: ChartPieIcon },
  { id: 'activities', label: 'Atividades complementares', icon: SparklesIcon },
  { id: 'internships', label: 'Estágio', icon: BriefcaseIcon },
  { id: 'final', label: 'TCC', icon: DocumentTextIcon },
];

export default function CompletionPage() {
  const { data, error, reload, submitActivity, withdrawActivity } = useMyCompletion();
  const [tab, setTab] = useState<CompletionTab>('requirements');
  useErrorToast(error, 'Erro ao carregar a integralização.');

  if (!data) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Integralização</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">O que falta para concluir: disciplinas, créditos, atividades, estágio e TCC.</p>
      </div>
      <TabNav tabs={tabs} active={tab} onChange={setTab} ariaLabel="Integralização" idPrefix="completion" />
      <div id={`completion-${tab}`} role="tabpanel" className="space-y-6">
        {tab === 'requirements' && (data.integralization.length === 0
          ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma matrícula em programa.</p>
          : data.integralization.map((item) => (
            <section key={item.program_enrollment_id} className={`${sectionCls} space-y-4`}>
              <h2 className="text-base font-semibold text-gray-900 dark:text-white">{item.program_name} · <span className="font-mono">{item.registration_number}</span></h2>
              <IntegralizationSummary integralization={item} />
            </section>
          )))}
        {tab === 'activities' && (
          <MyActivitiesSection activities={data.activities} enrollments={data.integralization} onSubmit={submitActivity} onWithdraw={withdrawActivity} />
        )}
        {tab === 'internships' && (
          <section className={`${sectionCls} space-y-4`}>
            {data.internships.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum estágio cadastrado pela secretaria.</p> : (
              <ul className="space-y-3">
                {data.internships.map((internship) => (
                  <InternshipCard key={internship.id} internship={internship}>
                    <InternshipLogs internshipId={internship.id} mode="student" canLog={internship.status === 'in_progress'} onChange={reload} />
                  </InternshipCard>
                ))}
              </ul>
            )}
          </section>
        )}
        {tab === 'final' && (
          <section className={`${sectionCls} space-y-3`}>
            {data.finalProjects.length === 0
              ? <p className="text-sm text-gray-500 dark:text-gray-400">TCC ainda não cadastrado.</p>
              : data.finalProjects.map((project) => <FinalProjectCard key={project.id} project={project} />)}
          </section>
        )}
      </div>
    </div>
  );
}
