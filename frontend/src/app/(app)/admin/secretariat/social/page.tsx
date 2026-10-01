'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import BenefitItemForm from '@/components/social/BenefitItemForm';
import FundingSourceForm from '@/components/social/FundingSourceForm';
import OfferingFundingRow from '@/components/social/OfferingFundingRow';
import StockEntryForm from '@/components/social/StockEntryForm';
import BackButton from '@/components/common/BackButton';
import { sectionCls } from '@/components/common/formStyles';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { benefitKindLabels, fundingKindLabels } from '@/lib/academic/socialLabels';
import { useBenefitItems } from '@/lib/hooks/social/useBenefitItems';
import { useFundingSources } from '@/lib/hooks/social/useFundingSources';
import { useOfferingFunding } from '@/lib/hooks/social/useOfferingFunding';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useCurrentRoles } from '@/lib/hooks/useCurrentRoles';

/** Programas sociais: financiadores, turmas financiadas, itens de beneficio e estoque. */
export default function SocialProgramsPage() {
  const router = useRouter();
  const { isAdmin, has } = useCurrentRoles();
  const coordination = isAdmin || has('coordinator');
  const { fundingSources, error, create } = useFundingSources();
  const { items, create: createItem, receive } = useBenefitItems();
  const { offerings, save } = useOfferingFunding();
  useErrorToast(error, 'Erro ao carregar os programas sociais.');

  return (
    <div className="space-y-6">
      <BackButton label="Secretaria" onClick={() => router.push('/admin/secretariat')} />
      <section className={`${sectionCls} space-y-4`}>
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Financiadores</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Quem financia as turmas e os benefícios; cada um tem sua prestação de contas.</p>
        </div>
        {coordination && <FundingSourceForm onSubmit={create} />}
        <ul className="divide-y divide-gray-100 dark:divide-gray-700">
          {fundingSources.map((funding) => (
            <li key={funding.id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
              <span className="text-gray-800 dark:text-gray-200">
                <strong className="text-gray-900 dark:text-white">{funding.name}</strong> · {fundingKindLabels[funding.kind]}
                {funding.agreement_number ? ` · ${funding.agreement_number}` : ''}{funding.amount_cents !== null ? ` · ${formatMoney(funding.amount_cents)}` : ''}
              </span>
              <Link href={`/admin/secretariat/social/funding/${funding.id}`} className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">Prestação de contas</Link>
            </li>
          ))}
        </ul>
      </section>
      {coordination && (
        <section className={`${sectionCls} space-y-2`}>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Turmas financiadas</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Com limite de faltas definido, o aluno que não consegue mais cumprir a frequência é desligado ao encerrar o encontro.</p>
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {offerings.map((offering) => (
              <OfferingFundingRow key={`${offering.id}-${offering.funding_source_id}-${offering.max_absence_percent}`} offering={offering}
                fundingSources={fundingSources} onSave={(fundingId, limit) => save(offering.id, fundingId, limit)} />
            ))}
          </ul>
        </section>
      )}
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Benefícios e estoque</h2>
        <BenefitItemForm onSubmit={createItem} />
        <ul className="divide-y divide-gray-100 dark:divide-gray-700">
          {items.map((item) => (
            <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
              <span className="text-gray-800 dark:text-gray-200">
                <strong className="text-gray-900 dark:text-white">{item.name}</strong> · {benefitKindLabels[item.kind]} · {formatMoney(item.unit_cost_cents)}/{item.unit}
                {item.requires_attendance ? ' · só presentes' : ''} · <span className={item.stock > 0 ? '' : 'text-red-600'}>estoque: {item.stock}</span>
              </span>
              <StockEntryForm item={item} fundingSources={fundingSources} onSubmit={(input) => receive(item.id, input)} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
