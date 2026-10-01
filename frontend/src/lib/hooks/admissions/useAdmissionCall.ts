'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { saveBlob } from '@/lib/files/saveBlob';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type {
  AdmissionCall, AdmissionCallStatus, Application, ApplicationDocument, ApplicationReviewInput, DeadlinesSummary, DocumentReview, SelectionSummary,
} from '@/types/admissions';

/** Um edital e suas inscricoes (secretaria): situacao, analise, comprovantes, selecao e prazos. */
export function useAdmissionCall(callId: number) {
  const request = useCallback(async () => {
    const [call, applications] = await Promise.all([
      api.get<AdmissionCall>(endpoints.admissions.call(callId)),
      api.get<Application[]>(endpoints.admissions.callApplications(callId)),
    ]);
    return { call: call.data, applications: applications.data };
  }, [callId]);
  const { data, error, reload } = useApiQuery(request);

  const run = async <T,>(action: () => Promise<T>) => {
    const result = await action();
    reload();
    return result;
  };

  return {
    call: data?.call,
    applications: data?.applications ?? [],
    error,
    changeStatus: (status: AdmissionCallStatus) => run(() => api.post(endpoints.admissions.callStatus(callId), { status })),
    review: (applicationId: number, input: ApplicationReviewInput) => run(() => api.post(endpoints.admissions.review(applicationId), input)),
    reviewDocument: (documentId: number, review: DocumentReview) => run(() => api.post(endpoints.admissions.documentReview(documentId), { review })),
    select: () => run(async () => (await api.post<SelectionSummary>(endpoints.admissions.select(callId))).data),
    processDeadlines: () => run(async () => (await api.post<DeadlinesSummary>(endpoints.admissions.deadlines(callId))).data),
    download: async (document: ApplicationDocument) => {
      const { data: blob } = await api.get<Blob>(endpoints.admissions.documentDownload(document.id), { responseType: 'blob' });
      saveBlob(blob, document.file_name);
    },
  };
}
