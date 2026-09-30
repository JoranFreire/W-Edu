import { ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function BackButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
    >
      <ArrowLeftIcon className="h-4 w-4" />
      <span>{label}</span>
    </button>
  );
}
