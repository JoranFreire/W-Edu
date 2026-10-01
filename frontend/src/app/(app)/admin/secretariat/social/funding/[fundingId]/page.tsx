'use client';

import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import FundingReportView from '@/components/social/FundingReportView';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { fundingKindLabels } from '@/lib/academic/socialLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useFundingReport } from '@/lib/hooks/social/useFundingReport';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Prestacao de contas de um financiador. */
export default function FundingReportPage() {
  const router = useRouter();
  const fundingId = Number(useParams<{ fundingId: string }>().fundingId);
  const { report, error, downloadCsv } = useFundingReport(fundingId);
  useErrorToast(error, 'Erro ao carregar a prestação de contas.');

  if (!report) return <Spinner />;
  return (
    <div className="space-y-6">
      <BackButton label="Programas sociais" onClick={() => router.push('/admin/secretariat/social')} />
      <section className={`${sectionCls} space-y-4`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Prestação de contas: {report.funding.name}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">{fundingKindLabels[report.funding.kind]}{report.funding.agreement_number ? ` · ${report.funding.agreement_number}` : ''}</p>
          </div>
          <button onClick={() => downloadCsv().catch((err) => toast.error(apiErrorMessage(err, 'Erro ao baixar.')))} className={secondaryButtonCls}>Baixar planilha (CSV)</button>
        </div>
        <FundingReportView report={report} />
      </section>
    </div>
  );
}
