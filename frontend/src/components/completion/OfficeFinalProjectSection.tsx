'use client';

import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { useEnrollmentFinalProject } from '@/lib/hooks/completion/useEnrollmentFinalProject';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { PersonSummary } from '@/types/academicGroups';
import FinalProjectCard from './FinalProjectCard';
import FinalProjectForm from './FinalProjectForm';

/** TCC da matricula: situacao atual e formulario de tema/orientacao. */
export default function OfficeFinalProjectSection({ enrollmentId, advisors, editable }: {
  enrollmentId: string;
  advisors: PersonSummary[];
  editable: boolean;
}) {
  const { project, loading, error, save } = useEnrollmentFinalProject(enrollmentId);
  useErrorToast(error, 'Erro ao carregar o TCC.');
  if (loading && !project) return <Spinner variant="panel" />;
  const canEdit = editable && project?.status !== 'approved';
  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Trabalho de conclusão (TCC)</h2>
      {project ? <FinalProjectCard project={project} /> : <p className="text-sm text-gray-500 dark:text-gray-400">TCC não cadastrado.</p>}
      {canEdit && <FinalProjectForm key={`${project?.id}-${project?.status}`} project={project} advisors={advisors} onSave={save} />}
    </section>
  );
}
