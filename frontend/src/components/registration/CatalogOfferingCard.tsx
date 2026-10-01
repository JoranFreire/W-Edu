import { formatSlot, situationCls, situationLabels } from '@/lib/academic/registrationLabels';
import { primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import type { CatalogOffering } from '@/types/registration';

export interface CatalogActions {
  onRegister: (offering: CatalogOffering) => void;
  onDrop: (offering: CatalogOffering) => void;
  /** Secretaria: inscreve dispensando pre-requisito, choque de horario e vagas. */
  onOverride?: (offering: CatalogOffering) => void;
}

/** Uma oferta do catalogo: horario, vagas, situacao do aluno, impedimentos e a acao possivel. */
export default function CatalogOfferingCard({ offering, actions }: { offering: CatalogOffering; actions?: CatalogActions }) {
  const { situation } = offering;
  const label = `${offering.subject.code} ${offering.offering_name}`;
  return (
    <li className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
            <span className="font-mono text-xs text-gray-500 dark:text-gray-400">{offering.subject.code}</span>
            {offering.subject.name}
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${situationCls[situation]}`}>
              {situationLabels[situation]}{offering.waitlist_position ? ` (${offering.waitlist_position}º)` : ''}
            </span>
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {[offering.offering_name, `${offering.credits} crédito(s)`, offering.instructor_name, `${offering.seats_taken}/${offering.capacity} vagas`]
              .filter(Boolean).join(' · ')}
          </p>
          <p className="text-xs text-gray-600 dark:text-gray-300">
            {offering.slots.length ? offering.slots.map(formatSlot).join(' · ') : 'Horário a definir'}
          </p>
          {offering.blockers.length > 0 && (
            <ul className="list-inside list-disc text-xs text-red-700 dark:text-red-300">
              {offering.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}
            </ul>
          )}
        </div>
        {actions && (
          <div className="flex shrink-0 flex-wrap gap-2">
            {(situation === 'enrolled' || situation === 'waitlisted') && (
              <button onClick={() => actions.onDrop(offering)} aria-label={`Cancelar ${label}`} className={secondaryButtonCls}>
                {situation === 'enrolled' ? 'Cancelar inscrição' : 'Sair da lista'}
              </button>
            )}
            {(situation === 'available' || situation === 'full') && (
              <button onClick={() => actions.onRegister(offering)} aria-label={`Inscrever em ${label}`} className={primaryButtonCls}>
                {situation === 'available' ? 'Inscrever' : 'Entrar na lista de espera'}
              </button>
            )}
            {actions.onOverride && (situation === 'blocked' || situation === 'full') && (
              <button onClick={() => actions.onOverride?.(offering)} aria-label={`Inscrever com exceção em ${label}`} className={secondaryButtonCls}>
                Inscrever com exceção
              </button>
            )}
          </div>
        )}
      </div>
    </li>
  );
}
