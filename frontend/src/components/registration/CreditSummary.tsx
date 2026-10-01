import type { RegistrationCatalog } from '@/types/registration';

/** Creditos inscritos no periodo frente ao minimo e maximo da janela. */
export default function CreditSummary({ catalog }: { catalog: RegistrationCatalog }) {
  const { credits_registered: credits, min_credits: min, max_credits: max } = catalog;
  const belowMin = min !== null && credits < min;
  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm text-gray-600 dark:text-gray-300">
      <span><strong className="text-gray-900 dark:text-white">{credits}</strong> crédito(s) inscrito(s)</span>
      {min !== null && <span>Mínimo: {min}</span>}
      {max !== null && <span>Máximo: {max}</span>}
      {belowMin && <span className="font-medium text-amber-700 dark:text-amber-300">Abaixo do mínimo de créditos do período</span>}
    </div>
  );
}
