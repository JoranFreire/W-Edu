import { resultLabels } from '@/lib/academic/assessmentLabels';
import type { ClassEnrollmentResult } from '@/types/assessment';

const styles: Record<ClassEnrollmentResult, string> = {
  in_progress: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  recovery: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  approved: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  failed: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
  failed_attendance: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
};

export default function ResultBadge({ result }: { result: ClassEnrollmentResult }) {
  return <span className={`w-fit whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ${styles[result]}`}>{resultLabels[result]}</span>;
}
