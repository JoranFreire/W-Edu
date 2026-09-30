'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type {
  AnalyticsOverview,
  AttendanceReportRow,
  ClassPerformanceReportRow,
  CompletionReportRow,
  CourseAnalytics,
  EngagementReportRow,
  RoiReportRow,
} from '@/types/analytics';

export interface AnalyticsReports {
  overview: AnalyticsOverview;
  courses: CourseAnalytics[];
  completion: CompletionReportRow[];
  attendance: AttendanceReportRow[];
  engagement: EngagementReportRow[];
  performance: ClassPerformanceReportRow[];
  roi: RoiReportRow[];
}

/** Visao geral e relatorios detalhados de analytics. */
export function useAnalyticsReports() {
  const request = useCallback(async (): Promise<AnalyticsReports> => {
    const [overview, courses, completion, attendance, engagement, performance, roi] = await Promise.all([
      api.get<AnalyticsOverview>(endpoints.analytics.overview),
      api.get<CourseAnalytics[]>(endpoints.analytics.courses),
      api.get<CompletionReportRow[]>(endpoints.analytics.reports.completion),
      api.get<AttendanceReportRow[]>(endpoints.analytics.reports.attendance),
      api.get<EngagementReportRow[]>(endpoints.analytics.reports.engagement),
      api.get<ClassPerformanceReportRow[]>(endpoints.analytics.reports.performance),
      api.get<RoiReportRow[]>(endpoints.analytics.reports.roi),
    ]);
    return {
      overview: overview.data,
      courses: courses.data,
      completion: completion.data,
      attendance: attendance.data,
      engagement: engagement.data,
      performance: performance.data,
      roi: roi.data,
    };
  }, []);
  return useApiQuery(request);
}
