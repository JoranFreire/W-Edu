'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BellIcon } from '@heroicons/react/24/outline';
import { useUnreadCount } from '@/lib/hooks/inbox/useUnreadCount';

/** Atalho para a caixa de avisos com a contagem de nao lidos (recontada a cada navegacao). */
export function InboxBell() {
  const pathname = usePathname();
  const unread = useUnreadCount(pathname);
  const label = unread > 0 ? `Avisos (${unread} não lido${unread > 1 ? 's' : ''})` : 'Avisos';
  return (
    <Link
      href="/notifications"
      aria-label={label}
      title={label}
      className="relative p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
    >
      <BellIcon className="w-5 h-5" />
      {unread > 0 && (
        <span className="absolute -right-0.5 -top-0.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-semibold text-white">
          {unread > 99 ? '99+' : unread}
        </span>
      )}
    </Link>
  );
}
