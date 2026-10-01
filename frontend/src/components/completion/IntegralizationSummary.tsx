import type { Integralization } from '@/types/completion';
import RequirementsList from './RequirementsList';

/** Cabecalho (CR e situacao) e requisitos de conclusao de uma matricula. */
export default function IntegralizationSummary({ integralization }: { integralization: Integralization }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm text-gray-600 dark:text-gray-300">
        <span>CR: <strong className="text-gray-900 dark:text-white">{integralization.cr ?? '—'}</strong></span>
        <span className={integralization.complete ? 'font-medium text-emerald-700 dark:text-emerald-300' : ''}>
          {integralization.complete ? 'Todos os requisitos cumpridos' : 'Requisitos pendentes'}
        </span>
      </div>
      <RequirementsList requirements={integralization.requirements} />
    </div>
  );
}
