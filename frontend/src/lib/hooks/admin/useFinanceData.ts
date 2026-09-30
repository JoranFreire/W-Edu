'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Organization, Student } from '@/types/auth';
import type { Course } from '@/types/course';
import type { BillingPlan, Charge, Subscription } from '@/types/finance';
import type { ClassOffering } from '@/types/schedule';

export interface FinanceData {
  plans: BillingPlan[];
  subscriptions: Subscription[];
  charges: Charge[];
  students: Student[];
  organizations: Organization[];
  courses: Course[];
  classes: ClassOffering[];
}

const empty: FinanceData = { plans: [], subscriptions: [], charges: [], students: [], organizations: [], courses: [], classes: [] };

/** Planos, assinaturas e cobrancas, com os cadastros usados nos formularios. */
export function useFinanceData() {
  const request = useCallback(async (): Promise<FinanceData> => {
    const [plans, subscriptions, charges, students, organizations, courses, classes] = await Promise.all([
      api.get<BillingPlan[]>(endpoints.finance.plans),
      api.get<Subscription[]>(endpoints.finance.subscriptions),
      api.get<Charge[]>(endpoints.finance.charges),
      api.get<Student[]>('/admin/users'),
      api.get<Organization[]>('/admin/organizations'),
      api.get<Course[]>(endpoints.courses.list),
      api.get<ClassOffering[]>(endpoints.schedule.classes),
    ]);
    return {
      plans: plans.data,
      subscriptions: subscriptions.data,
      charges: charges.data,
      students: students.data,
      organizations: organizations.data,
      courses: courses.data,
      classes: classes.data,
    };
  }, []);
  const { data = empty, loading, error, reload } = useApiQuery(request);
  return { ...data, loading, error, reload };
}
