import { EmptyPanel, Stat } from '@/components/admin/users/dossier/DossierParts';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { chargeStatusLabels } from '@/lib/finance/labels';
import type { DossierFinance } from '@/types/userDossier';

const thCls = 'px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400';
const tdCls = 'px-4 py-2 text-sm text-gray-900 dark:text-white';
const formatDate = (value: string | null) => (value ? new Date(value).toLocaleDateString('pt-BR') : '—');

/** Resumo das cobrancas em aberto e o extrato recente (como aluno ou responsavel financeiro). */
export default function FinanceTab({ finance }: { finance: DossierFinance }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Em aberto" value={formatMoney(finance.open_cents)} />
        <Stat label="Parcelas em aberto" value={finance.open_count} />
        <Stat label="Vencidas" value={finance.overdue_count} tone={finance.overdue_count > 0 ? 'danger' : 'default'} />
        <Stat label="Próximo vencimento" value={formatDate(finance.next_due_at)} />
      </div>
      {finance.charges.length === 0 ? <EmptyPanel>Nenhuma cobrança.</EmptyPanel> : (
        <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
          <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
            <thead><tr><th className={thCls}>Vencimento</th><th className={thCls}>Descrição</th><th className={thCls}>Valor</th><th className={thCls}>Situação</th><th className={thCls}>Pagamento</th></tr></thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {finance.charges.map((charge) => (
                <tr key={charge.id}>
                  <td className={tdCls}>{formatDate(charge.due_at)}</td>
                  <td className={tdCls}>
                    {charge.description || (charge.installment_number ? `Parcela ${charge.installment_number}` : 'Cobrança')}
                    {charge.as_payer && <span className="ml-1 text-xs text-gray-500 dark:text-gray-400">(como responsável)</span>}
                  </td>
                  <td className={tdCls}>{formatMoney(charge.amount_cents)}</td>
                  <td className={tdCls}>{chargeStatusLabels[charge.status] ?? charge.status}</td>
                  <td className={tdCls}>{formatDate(charge.paid_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
