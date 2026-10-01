import type { Requirement } from '@/types/completion';

function progressOf(requirement: Requirement): number {
  if (requirement.required <= 0) return 100;
  return Math.min(100, Math.round((100 * requirement.done) / requirement.required));
}

function amount(requirement: Requirement): string {
  if (requirement.key === 'final_project') return requirement.met ? 'Aprovado' : 'Pendente';
  const unit = requirement.unit === 'h' ? 'h' : ` ${requirement.unit}`;
  return `${requirement.done}${unit} de ${requirement.required}${unit}`;
}

/** Requisitos de conclusao com barra de progresso. */
export default function RequirementsList({ requirements }: { requirements: Requirement[] }) {
  return (
    <ul className="space-y-3">
      {requirements.map((requirement) => (
        <li key={requirement.key} className="space-y-1">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="font-medium text-gray-900 dark:text-white">{requirement.label}</span>
            <span className={requirement.met ? 'text-emerald-700 dark:text-emerald-300' : 'text-gray-600 dark:text-gray-300'}>{amount(requirement)}</span>
          </div>
          <div className="h-2 rounded-full bg-gray-100 dark:bg-gray-700" role="progressbar" aria-label={requirement.label}
            aria-valuenow={progressOf(requirement)} aria-valuemin={0} aria-valuemax={100}>
            <div className={`h-2 rounded-full ${requirement.met ? 'bg-emerald-500' : 'bg-indigo-500'}`} style={{ width: `${progressOf(requirement)}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}
