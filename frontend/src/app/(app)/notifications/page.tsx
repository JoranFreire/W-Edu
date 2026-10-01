'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import InboxList from '@/components/inbox/InboxList';
import Spinner from '@/components/common/Spinner';
import { inputCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useInbox } from '@/lib/hooks/inbox/useInbox';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { InboxNotice } from '@/types/notification';

export default function NotificationsPage() {
  const [unreadOnly, setUnreadOnly] = useState(false);
  const { notices, loading, error, markRead, markAllRead } = useInbox(unreadOnly);
  useErrorToast(error, 'Erro ao carregar avisos.');

  const run = async (action: () => Promise<void>) => {
    try {
      await action();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível atualizar o aviso.'));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Avisos</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Comunicados da instituição: ocorrências, agenda, boletim e outros.</p>
        </div>
        <div className="flex items-center gap-2">
          <select aria-label="Filtrar avisos" value={unreadOnly ? 'unread' : 'all'} onChange={(e) => setUnreadOnly(e.target.value === 'unread')} className={inputCls}>
            <option value="all">Todos</option>
            <option value="unread">Não lidos</option>
          </select>
          <button onClick={() => run(markAllRead)} className={`${secondaryButtonCls} shrink-0`}>Marcar todos como lidos</button>
        </div>
      </div>
      <section className={sectionCls}>
        {loading && notices.length === 0
          ? <Spinner />
          : <InboxList notices={notices} onMarkRead={(notice: InboxNotice) => run(() => markRead(notice.id))} />}
      </section>
    </div>
  );
}
