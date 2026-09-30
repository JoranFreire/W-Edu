import { curriculumStatusLabels } from '@/lib/academic/labels';
import type { CurriculumStatus } from '@/types/academic';

const styles: Record<CurriculumStatus, string> = {
  draft: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  active: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  archived: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

export default function CurriculumStatusBadge({ status }: { status: CurriculumStatus }) {
  return <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${styles[status]}`}>{curriculumStatusLabels[status]}</span>;
}
