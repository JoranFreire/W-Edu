import type { NotificationEvent } from '@/types/notification';

export default function NotificationEventsList({ events, onMarkSent, onMarkFailed }: {
  events: NotificationEvent[];
  onMarkSent: (event: NotificationEvent) => void;
  onMarkFailed: (event: NotificationEvent) => void;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      {events.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhum evento registrado.</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {events.map((event) => (
            <div key={event.id} className="px-5 py-4 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{event.event_type}</p>
                  <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300">{event.status}</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 break-all">{event.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 break-all">{event.body}</p>
                {event.scheduled_for && <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Agendado para {new Date(event.scheduled_for).toLocaleString('pt-BR')}</p>}
              </div>
              <div className="flex shrink-0 gap-2">
                <button onClick={() => onMarkSent(event)} className="px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300">Enviado</button>
                <button onClick={() => onMarkFailed(event)} className="px-3 py-1.5 text-xs font-medium rounded-lg bg-red-600 hover:bg-red-700 text-white">Falhou</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
