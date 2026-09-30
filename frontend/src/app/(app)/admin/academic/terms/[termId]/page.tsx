'use client';

import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import CalendarPanel from '@/components/admin/academic/terms/CalendarPanel';
import GradingPeriodsPanel from '@/components/admin/academic/terms/GradingPeriodsPanel';
import TermStatusActions from '@/components/admin/academic/terms/TermStatusActions';
import TermStatusBadge from '@/components/admin/academic/terms/TermStatusBadge';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { termKindLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';
import type { TermStatus } from '@/types/academicCalendar';

export default function AdminTermPage() {
  const router = useRouter();
  const termId = Number(useParams<{ termId: string }>().termId);
  const canDelete = isAdminRole(useAuthStore((state) => state.student?.role));
  const { terms, error, changeStatus } = useAcademicTerms();
  useErrorToast(error, 'Erro ao carregar período.');
  const term = terms.find((item) => item.id === termId);

  const handleStatus = async (target: TermStatus) => {
    try {
      await changeStatus(termId, target);
      toast.success('Situação do período atualizada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível alterar o período.'));
    }
  };

  if (!term) return <Spinner />;
  const editable = term.status !== 'closed';
  return (
    <div className="space-y-6">
      <BackButton label="Estrutura acadêmica" onClick={() => router.push('/admin/academic')} />
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white">
            {term.name} <TermStatusBadge status={term.status} />
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {termKindLabels[term.kind]} · {formatIsoDate(term.starts_on)} a {formatIsoDate(term.ends_on)}
          </p>
        </div>
        <TermStatusActions status={term.status} onChange={handleStatus} />
      </div>
      <GradingPeriodsPanel key={`periods-${term.status}`} termId={termId} editable={editable} canDelete={canDelete} />
      <CalendarPanel termId={termId} editable={editable} />
    </div>
  );
}
