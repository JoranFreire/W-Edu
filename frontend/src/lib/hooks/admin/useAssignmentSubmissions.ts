'use client';

import { useCallback, useState } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { AssignmentSubmission, AssignmentSubmissionStatus } from '@/types/assignment';

export interface SubmissionReview {
  status: AssignmentSubmissionStatus;
  score: number | null;
  feedback: string | null;
}

/** Entregas de uma aula e a correcao de cada uma. */
export function useAssignmentSubmissions(lessonId: number) {
  const request = useCallback(
    () => api.get<AssignmentSubmission[]>(endpoints.assignments.submissions(lessonId)).then((response) => response.data),
    [lessonId],
  );
  const query = useApiQuery(request);
  const [reviewed, setReviewed] = useState<Record<number, AssignmentSubmission>>({});

  const review = async (submissionId: number, data: SubmissionReview) => {
    const { data: updated } = await api.patch<AssignmentSubmission>(endpoints.assignments.review(submissionId), data);
    setReviewed((current) => ({ ...current, [submissionId]: updated }));
  };

  const submissions = (query.data ?? []).map((submission) => reviewed[submission.id] ?? submission);
  return { submissions, loading: query.loading, error: query.error, review };
}
