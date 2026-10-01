'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import type { SubmissionReview } from '@/lib/hooks/admin/useAssignmentSubmissions';
import type { AssignmentSubmission, AssignmentSubmissionStatus } from '@/types/assignment';

const statusLabels: Record<AssignmentSubmissionStatus, string> = {
  submitted: 'Enviada',
  reviewed: 'Corrigida',
  returned: 'Devolvida',
};
const fieldCls = 'rounded-lg border border-gray-300 bg-white px-2 py-2 text-xs text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white';

export default function SubmissionReviewRow({ submission, onDownload, onReview }: {
  submission: AssignmentSubmission;
  onDownload: (submission: AssignmentSubmission) => void;
  onReview: (submissionId: string, review: SubmissionReview) => Promise<void>;
}) {
  const [status, setStatus] = useState(submission.status);
  const [score, setScore] = useState(submission.score === null ? '' : String(submission.score));
  const [feedback, setFeedback] = useState(submission.feedback ?? '');
  const [saving, setSaving] = useState(false);

  const save = async () => {
    const parsedScore = score.trim() === '' ? null : Number(score);
    if (parsedScore !== null && (Number.isNaN(parsedScore) || parsedScore < 0 || parsedScore > 100)) {
      toast.error('Nota deve ficar entre 0 e 100.');
      return;
    }
    setSaving(true);
    try {
      await onReview(submission.id, { status, score: parsedScore, feedback: feedback.trim() || null });
      toast.success('Entrega corrigida.');
    } catch {
      toast.error('Erro ao salvar correção.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3 p-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-gray-900 dark:text-white">Aluno #{submission.student_id}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {statusLabels[submission.status]} em {new Date(submission.submitted_at).toLocaleString('pt-BR')}
          </p>
        </div>
        {submission.file_name && (
          <button type="button" onClick={() => onDownload(submission)} className="w-fit rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
            Baixar arquivo
          </button>
        )}
      </div>
      {submission.text && (
        <p className="rounded-lg bg-gray-50 p-3 text-sm text-gray-700 dark:bg-gray-900 dark:text-gray-300 whitespace-pre-wrap">{submission.text}</p>
      )}
      <div className="grid grid-cols-1 gap-2 md:grid-cols-[140px_100px_1fr_auto] md:items-start">
        <select value={status} onChange={(event) => setStatus(event.target.value as AssignmentSubmissionStatus)} aria-label="Status da entrega" className={`${fieldCls} px-2`}>
          {Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
        <input type="number" min={0} max={100} value={score} onChange={(event) => setScore(event.target.value)} placeholder="Nota" className={fieldCls} />
        <textarea rows={2} value={feedback} onChange={(event) => setFeedback(event.target.value)} placeholder="Feedback" className={fieldCls} />
        <button type="button" onClick={save} disabled={saving} className="rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
          {saving ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </div>
  );
}
