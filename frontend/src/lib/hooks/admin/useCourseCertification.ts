'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { Enrollment } from '@/types/course';
import type { Certificate, CertificateEligibility, CertificateIssueResult, CertificateRule } from '@/types/certificate';

interface CourseCertificationData {
  rule: CertificateRule;
  certificates: Certificate[];
  enrollments: Enrollment[];
}

/** Regra, certificados emitidos e matriculas de um curso, com emissao e revogacao. */
export function useCourseCertification(courseId: string) {
  const request = useCallback(async (): Promise<CourseCertificationData> => {
    const [rule, certificates, enrollments] = await Promise.all([
      api.get<CertificateRule>(endpoints.certificates.rule(courseId)),
      api.get<Certificate[]>(endpoints.certificates.courseCertificates(courseId)),
      api.get<Enrollment[]>(`/admin/enrollments/course/${courseId}`),
    ]);
    return { rule: rule.data, certificates: certificates.data, enrollments: enrollments.data };
  }, [courseId]);
  const { data, loading, error, reload } = useApiQuery(request);

  const saveRule = async (rule: CertificateRule) => {
    const { data: saved } = await api.patch<CertificateRule>(endpoints.certificates.rule(courseId), rule);
    return saved;
  };
  const checkEligibility = async (studentId: string) => {
    const { data: eligibility } = await api.get<CertificateEligibility>(endpoints.certificates.eligibility(courseId, studentId));
    return eligibility;
  };
  const issue = async (studentId: string) => {
    const { data: result } = await api.post<CertificateIssueResult>(endpoints.certificates.issue(courseId, studentId));
    reload();
    return result;
  };
  const revoke = async (certificateId: string, reason: string | null) => {
    await api.post<Certificate>(endpoints.certificates.revoke(certificateId), { reason });
    reload();
  };

  return { data, loading, error, saveRule, checkEligibility, issue, revoke };
}
