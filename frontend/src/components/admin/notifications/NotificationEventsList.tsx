import { ArrowPathIcon } from '@heroicons/react/24/outline';
import { secondaryButtonCls } from '@/components/common/formStyles';
import { notificationChannelLabels, notificationEventLabel, notificationStatusLabels } from '@/lib/notifications/labels';
import type { NotificationEvent, NotificationStatus } from '@/types/notification';

const statusCls: Record<NotificationStatus, string> = {
  pending: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  sent: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  failed: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
};

const formatDateTime = (value: string) => new Date(value).toLocaleString('pt-BR');

/** Quando o evento foi (ou sera) entregue, conforme a situacao. */
function deliveryNote(event: NotificationEvent): string | null {
  if (event.status === 'sent' && event.sent_at) return `Enviado em ${formatDateTime(event.sent_at)}`;
  if (event.status === 'pending' && event.scheduled_for) return `Agendado para ${formatDateTime(event.scheduled_for)}`;
  if (event.status === 'pending') return 'Na fila de envio';
  return null;
}

/** Fila de eventos: a entrega e automatica; o admin acompanha e reenvia os que falharam. */
export default function NotificationEventsList({ events, onRetry }: {
  events: NotificationEvent[];
  onRetry: (event: NotificationEvent) => void;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      {events.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhum evento registrado.</p>
      ) : (
        <ul aria-label="Eventos" className="divide-y divide-gray-100 dark:divide-gray-700">
          {events.map((event) => {
            const note = deliveryNote(event);
            return (
              <li key={event.id} className="flex items-start justify-between gap-4 px-5 py-4">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">{event.title}</p>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusCls[event.status]}`}>{notificationStatusLabels[event.status]}</span>
                  </div>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{notificationEventLabel(event.event_type)} · {notificationChannelLabels[event.channel]}</p>
                  <p className="mt-1 break-words text-xs text-gray-500 dark:text-gray-400">{event.body}</p>
                  {event.status === 'failed' && event.error_message && (
                    <p className="mt-1 text-xs text-red-600 dark:text-red-400">Motivo da falha: {event.error_message}</p>
                  )}
                  {note && <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">{note}</p>}
                </div>
                {event.status === 'failed' && (
                  <button type="button" onClick={() => onRetry(event)} className={`${secondaryButtonCls} shrink-0 !px-3 !py-1.5 text-xs`}>
                    <ArrowPathIcon className="h-4 w-4" /><span>Tentar novamente</span>
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
