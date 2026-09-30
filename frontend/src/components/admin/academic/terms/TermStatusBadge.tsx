import { termStatusLabels } from '@/lib/academic/labels';
import type { TermStatus } from '@/types/academicCalendar';

const styles: Record<TermStatus, string> = {
  planned: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  open: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  closed: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

export default function TermStatusBadge({ status }: { status: TermStatus }) {
  return <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${styles[status]}`}>{termStatusLabels[status]}</span>;
}
