'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { ReportCardEntry } from '@/types/assessment';
import type { DependentCharge, DependentNotice } from '@/types/guardians';

interface DependentOverview {
  reportCard: ReportCardEntry[];
  notices: DependentNotice[];
  charges: DependentCharge[] | null;
}

/** Boletim, comunicados e (para o responsavel financeiro) cobrancas de um dependente. */
export function useDependentOverview(studentId: string, isFinancial: boolean) {
  const request = useCallback(async (): Promise<DependentOverview> => {
    const [reportCard, notices, charges] = await Promise.all([
      api.get<ReportCardEntry[]>(endpoints.guardians.reportCard(studentId)),
      api.get<DependentNotice[]>(endpoints.guardians.notices(studentId)),
      isFinancial ? api.get<DependentCharge[]>(endpoints.guardians.charges(studentId)) : Promise.resolve(null),
    ]);
    return { reportCard: reportCard.data, notices: notices.data, charges: charges ? charges.data : null };
  }, [studentId, isFinancial]);
  const { data, loading, error } = useApiQuery(request);
  return { overview: data, loading, error };
}
