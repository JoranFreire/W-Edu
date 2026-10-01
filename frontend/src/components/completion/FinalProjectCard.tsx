import type { ReactNode } from 'react';
import { finalProjectStatusLabels } from '@/lib/academic/completionLabels';
import { formatIsoDate } from '@/lib/dates';
import type { FinalProject } from '@/types/completion';

/** Resumo do TCC: tema, orientacao, situacao e, depois da defesa, data, nota e banca. */
export default function FinalProjectCard({ project, showStudent = false, children }: {
  project: FinalProject;
  showStudent?: boolean;
  children?: ReactNode;
}) {
  return (
    <div className="space-y-2 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <p className="font-medium text-gray-900 dark:text-white">{showStudent ? `${project.student.name} · ` : ''}{project.title}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        {[finalProjectStatusLabels[project.status], project.advisor ? `Orientação: ${project.advisor.name}` : 'Sem orientador',
          project.co_advisor_name ? `Coorientação: ${project.co_advisor_name}` : null].filter(Boolean).join(' · ')}
      </p>
      {project.defense_on && (
        <p className="text-sm text-gray-700 dark:text-gray-200">
          Defesa em {formatIsoDate(project.defense_on)}{project.grade !== null ? ` · nota ${project.grade}` : ''}{project.committee ? ` · banca: ${project.committee}` : ''}
        </p>
      )}
      {children}
    </div>
  );
}
