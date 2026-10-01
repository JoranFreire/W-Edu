import { CheckIcon } from '@heroicons/react/24/outline';
import { secondaryButtonCls } from '@/components/common/formStyles';
import type { InboxNotice } from '@/types/notification';

/** Avisos do usuario; os nao lidos ficam destacados e podem ser marcados como lidos. */
export default function InboxList({ notices, onMarkRead }: {
  notices: InboxNotice[];
  onMarkRead: (notice: InboxNotice) => void;
}) {
  if (notices.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aviso.</p>;
  return (
    <ul className="space-y-3">
      {notices.map((notice) => {
        const unread = notice.read_at === null;
        return (
          <li
            key={notice.id}
            className={`flex items-start justify-between gap-3 rounded-lg border p-4 ${
              unread ? 'border-indigo-200 bg-indigo-50/60 dark:border-indigo-800 dark:bg-indigo-900/20' : 'border-gray-200 dark:border-gray-700'
            }`}
          >
            <div className="space-y-1">
              <p className="font-medium text-gray-900 dark:text-white">{notice.title}</p>
              <p className="text-sm text-gray-600 dark:text-gray-300">{notice.body}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(notice.created_at).toLocaleString('pt-BR')}</p>
            </div>
            {unread && (
              <button onClick={() => onMarkRead(notice)} aria-label={`Marcar como lido: ${notice.title}`} className={secondaryButtonCls}>
                <CheckIcon className="h-4 w-4" /> Lido
              </button>
            )}
          </li>
        );
      })}
    </ul>
  );
}
