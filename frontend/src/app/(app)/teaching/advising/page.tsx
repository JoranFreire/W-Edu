'use client';

import { useRouter } from 'next/navigation';
import FinalProjectCard from '@/components/completion/FinalProjectCard';
import FinalProjectResultForm from '@/components/completion/FinalProjectResultForm';
import InternshipCard from '@/components/completion/InternshipCard';
import InternshipLogs from '@/components/completion/InternshipLogs';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { useAdvising } from '@/lib/hooks/completion/useAdvising';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Orientacoes do docente: valida as horas de estagio e registra entrega e defesa do TCC. */
export default function AdvisingPage() {
  const router = useRouter();
  const { advising, error, reload, recordResult } = useAdvising();
  useErrorToast(error, 'Erro ao carregar as orientações.');

  if (!advising) return <Spinner />;
  return (
    <div className="space-y-6">
      <BackButton label="Minhas turmas" onClick={() => router.push('/teaching')} />
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Orientações</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Estágios em andamento e trabalhos de conclusão que você orienta.</p>
      </div>
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Estágios</h2>
        {advising.internships.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum estágio em andamento.</p> : (
          <ul className="space-y-3">
            {advising.internships.map((internship) => (
              <InternshipCard key={internship.id} internship={internship} showStudent>
                <InternshipLogs internshipId={internship.id} mode="advisor" onChange={reload} />
              </InternshipCard>
            ))}
          </ul>
        )}
      </section>
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Trabalhos de conclusão</h2>
        {advising.final_projects.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum TCC em andamento.</p> : (
          advising.final_projects.map((project) => (
            <FinalProjectCard key={project.id} project={project} showStudent>
              <FinalProjectResultForm project={project} onRecord={(input) => recordResult(project.id, input)} />
            </FinalProjectCard>
          ))
        )}
      </section>
    </div>
  );
}
