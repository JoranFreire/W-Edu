import type { DependentNotice } from '@/types/guardians';

export default function DependentNotices({ notices }: { notices: DependentNotice[] }) {
  if (notices.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum comunicado.</p>;
  return (
    <ul className="space-y-3">
      {notices.map((notice) => (
        <li key={notice.id} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="font-medium text-gray-900 dark:text-white">{notice.title}</p>
          <p className="text-sm text-gray-600 dark:text-gray-300">{notice.body}</p>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{new Date(notice.created_at).toLocaleString('pt-BR')}</p>
        </li>
      ))}
    </ul>
  );
}
