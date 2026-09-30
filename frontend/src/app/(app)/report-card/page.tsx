'use client';

import ReportCardList from '@/components/reportCard/ReportCardList';
import Spinner from '@/components/common/Spinner';
import { useReportCard } from '@/lib/hooks/useReportCard';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function ReportCardPage() {
  const { entries, loading, error } = useReportCard();
  useErrorToast(error, 'Erro ao carregar boletim.');

  if (loading && entries.length === 0) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Boletim</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Médias das etapas fechadas e resultado final publicado.</p>
      </div>
      <ReportCardList entries={entries} />
    </div>
  );
}
