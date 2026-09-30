'use client';

import { useState } from 'react';
import { ArrowPathIcon, ChartBarIcon, ClipboardDocumentCheckIcon, CurrencyDollarIcon, PresentationChartLineIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import { useAnalyticsReports } from '@/lib/hooks/admin/useAnalyticsReports';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import AnalyticsOverviewSection from '@/components/admin/AnalyticsOverviewSection';
import { AttendanceTable, CompletionTable, EngagementTable, PerformanceTable, RoiTable } from '@/components/admin/AnalyticsReportsTables';
import Spinner from '@/components/common/Spinner';

type ReportTab = 'completion' | 'attendance' | 'engagement' | 'performance' | 'roi';

export default function AdminAnalyticsPage() {
  const { data: reports, loading, error, reload } = useAnalyticsReports();
  const [activeTab, setActiveTab] = useState<ReportTab>('completion');

  useErrorToast(error, 'Erro ao carregar relatórios.');

  const tabs = [
    { id: 'completion' as ReportTab, label: 'Conclusão', icon: ClipboardDocumentCheckIcon, badge: reports?.completion.length ?? 0 },
    { id: 'attendance' as ReportTab, label: 'Presença', icon: UserGroupIcon, badge: reports?.attendance.length ?? 0 },
    { id: 'engagement' as ReportTab, label: 'Engajamento', icon: ChartBarIcon, badge: reports?.engagement.length ?? 0 },
    { id: 'performance' as ReportTab, label: 'Performance', icon: PresentationChartLineIcon, badge: reports?.performance.length ?? 0 },
    { id: 'roi' as ReportTab, label: 'ROI', icon: CurrencyDollarIcon, badge: reports?.roi.length ?? 0 },
  ];

  if (loading || !reports) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Relatórios</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Visão executiva de operação, conclusão, presença e receita.</p>
        </div>
        <button onClick={reload} className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200">
          <ArrowPathIcon className="w-4 h-4" /><span>Atualizar</span>
        </button>
      </div>

      <AnalyticsOverviewSection overview={reports.overview} courses={reports.courses} />

      <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Relatórios detalhados</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Clique no recorte desejado para carregar o relatório abaixo.</p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-5">
          <div className="rounded-xl bg-gray-50 p-1 dark:bg-gray-900/40 sm:col-span-2 xl:col-span-5">
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-5">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center justify-between gap-3 rounded-lg px-3 py-3 text-left text-sm font-medium transition-colors ${
                    active
                      ? 'bg-white text-blue-600 shadow-sm ring-1 ring-gray-200 dark:bg-gray-800 dark:text-blue-400 dark:ring-gray-700'
                      : 'text-gray-500 hover:bg-white hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'
                  }`}
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <Icon className="h-4 w-4 shrink-0" />
                    <span>{tab.label}</span>
                  </span>
                  <span
                    className={`inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-medium ${
                      active
                        ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {tab.badge}
                  </span>
                </button>
              );
            })}
            </div>
          </div>
        </div>

        <div className="mt-5" id={`report-${activeTab}`}>
          {activeTab === 'completion' && <CompletionTable rows={reports.completion} />}
          {activeTab === 'attendance' && <AttendanceTable rows={reports.attendance} />}
          {activeTab === 'engagement' && <EngagementTable rows={reports.engagement} />}
          {activeTab === 'performance' && <PerformanceTable rows={reports.performance} />}
          {activeTab === 'roi' && <RoiTable rows={reports.roi} />}
        </div>
      </div>
    </div>
  );
}
