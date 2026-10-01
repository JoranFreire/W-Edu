import { EmptyPanel } from '@/components/admin/users/dossier/DossierParts';
import { formatIsoDate } from '@/lib/dates';
import type { DossierBenefit } from '@/types/userDossier';

const thCls = 'px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400';
const tdCls = 'px-4 py-2 text-sm text-gray-900 dark:text-white';

/** Beneficios recebidos (lanche, kit, transporte) nas turmas de programas sociais. */
export default function BenefitsTab({ benefits }: { benefits: DossierBenefit[] }) {
  if (benefits.length === 0) return <EmptyPanel>Nenhum benefício recebido.</EmptyPanel>;
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
        <thead><tr><th className={thCls}>Data</th><th className={thCls}>Item</th><th className={thCls}>Quantidade</th><th className={thCls}>Turma</th></tr></thead>
        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
          {benefits.map((benefit) => (
            <tr key={benefit.id}>
              <td className={tdCls}>{formatIsoDate(benefit.delivered_on)}</td>
              <td className={tdCls}>{benefit.item_name}</td>
              <td className={tdCls}>{benefit.quantity} {benefit.unit}</td>
              <td className={tdCls}>{benefit.offering_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
