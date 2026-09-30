'use client';

import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { saveBlob } from '@/lib/files/saveBlob';
import { useAssignmentSubmissions } from '@/lib/hooks/admin/useAssignmentSubmissions';
import SubmissionReviewRow from '@/components/admin/assignments/SubmissionReviewRow';
import type { AssignmentSubmission } from '@/types/assignment';

async function downloadSubmission(submission: AssignmentSubmission) {
  if (!submission.file_name) return;
  try {
    const { data } = await api.get(endpoints.assignments.download(submission.id), { responseType: 'blob' });
    saveBlob(data, submission.file_name);
  } catch {
    toast.error('Erro ao baixar arquivo.');
  }
}

export default function AssignmentSubmissionsPanel({ lessonId }: { lessonId: number }) {
  const { submissions, loading, error, review } = useAssignmentSubmissions(lessonId);

  if (loading) return <p className="p-3 text-xs text-gray-500 dark:text-gray-400">Carregando entregas...</p>;
  if (error) return <p className="p-3 text-xs text-red-600 dark:text-red-400">Erro ao carregar entregas.</p>;
  if (submissions.length === 0) return <p className="p-3 text-xs text-gray-500 dark:text-gray-400">Nenhuma entrega enviada.</p>;

  return (
    <div className="divide-y divide-gray-100 dark:divide-gray-700">
      {submissions.map((submission) => (
        <SubmissionReviewRow key={submission.id} submission={submission} onDownload={downloadSubmission} onReview={review} />
      ))}
    </div>
  );
}
