import type { ReactNode } from 'react';
import { internshipStatusLabels } from '@/lib/academic/completionLabels';
import { formatIsoDate } from '@/lib/dates';
import type { Internship } from '@/types/completion';

/** Resumo do estagio (concedente, orientador, periodo e horas) com area livre para o diario e acoes. */
export default function InternshipCard({ internship, showStudent = false, children }: {
  internship: Internship;
  showStudent?: boolean;
  children?: ReactNode;
}) {
  const period = `${formatIsoDate(internship.starts_on)}${internship.ends_on ? ` a ${formatIsoDate(internship.ends_on)}` : ''}`;
  return (
    <li className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="space-y-1">
        <p className="font-medium text-gray-900 dark:text-white">
          {showStudent ? `${internship.student.name} · ` : ''}{internship.company_name}
          <span className="ml-2 text-xs font-normal text-gray-500 dark:text-gray-400">
            {internshipStatusLabels[internship.status]} · {internship.is_mandatory ? 'obrigatório' : 'não obrigatório'}
          </span>
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {[period, internship.advisor ? `Orientação: ${internship.advisor.name}` : null, internship.supervisor_name ? `Supervisão: ${internship.supervisor_name}` : null,
            internship.agreement_number ? `Termo ${internship.agreement_number}` : null].filter(Boolean).join(' · ')}
        </p>
        <p className="text-sm text-gray-700 dark:text-gray-200">
          {internship.approved_hours}h validadas{internship.planned_hours ? ` de ${internship.planned_hours}h previstas` : ''}
          {internship.pending_hours > 0 ? ` · ${internship.pending_hours}h aguardando validação` : ''}
        </p>
      </div>
      {children}
    </li>
  );
}
