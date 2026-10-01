import type { RegistrationCatalog } from '@/types/registration';
import CatalogOfferingCard, { type CatalogActions } from './CatalogOfferingCard';
import CreditSummary from './CreditSummary';

/** Resumo de creditos e ofertas do periodo; sem `actions`, so leitura (janela fechada). */
export default function RegistrationCatalogView({ catalog, actions }: { catalog: RegistrationCatalog; actions?: CatalogActions }) {
  return (
    <div className="space-y-4">
      <CreditSummary catalog={catalog} />
      {catalog.offerings.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma oferta aberta para as disciplinas da matriz neste período.</p>
      ) : (
        <ul className="space-y-3">
          {catalog.offerings.map((offering) => <CatalogOfferingCard key={offering.offering_id} offering={offering} actions={actions} />)}
        </ul>
      )}
    </div>
  );
}
