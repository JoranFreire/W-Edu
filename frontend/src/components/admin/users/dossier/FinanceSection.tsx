import { BanknotesIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import { formatMoney } from '@/lib/academic/guardianLabels';
import type { UserDossier } from '@/types/userDossier';

/** Resumo das cobrancas em aberto (como aluno ou como responsavel financeiro). */
export default function FinanceSection({ finance }: { finance: NonNullable<UserDossier['finance']> }) {
  return (
    <DossierSection title="Financeiro" icon={BanknotesIcon} isEmpty={finance.open_count === 0} emptyText="Nenhuma cobrança em aberto.">
      <dl className="grid grid-cols-2 gap-3 text-sm">
        <div><dt className="text-xs text-gray-500 dark:text-gray-400">Em aberto</dt><dd className="font-medium text-gray-900 dark:text-white">{finance.open_count} · {formatMoney(finance.open_cents)}</dd></div>
        <div>
          <dt className="text-xs text-gray-500 dark:text-gray-400">Vencidas</dt>
          <dd className={`font-medium ${finance.overdue_count > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>{finance.overdue_count}</dd>
        </div>
        {finance.next_due_at && (
          <div className="col-span-2"><dt className="text-xs text-gray-500 dark:text-gray-400">Próximo vencimento</dt><dd className="text-gray-900 dark:text-white">{new Date(finance.next_due_at).toLocaleDateString('pt-BR')}</dd></div>
        )}
      </dl>
    </DossierSection>
  );
}
