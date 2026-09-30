import { enrollmentEventLabels } from '@/lib/academic/secretariatLabels';
import type { EnrollmentEvent } from '@/types/secretariat';

function describe(event: EnrollmentEvent): string | null {
  const destination = event.details.destination;
  return typeof destination === 'string' ? `Destino: ${destination}` : null;
}

/** Linha do tempo das movimentacoes da matricula. */
export default function EnrollmentTimeline({ events }: { events: EnrollmentEvent[] }) {
  if (events.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Sem movimentações.</p>;
  return (
    <ol className="space-y-3 border-l border-gray-200 pl-4 dark:border-gray-700">
      {[...events].reverse().map((event) => (
        <li key={event.id} className="relative">
          <span className="absolute -left-[1.3rem] top-1.5 h-2.5 w-2.5 rounded-full bg-indigo-500" />
          <p className="text-sm font-medium text-gray-900 dark:text-white">{enrollmentEventLabels[event.kind]}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(event.created_at).toLocaleString('pt-BR')}</p>
          {[event.reason, describe(event)].filter(Boolean).map((text) => (
            <p key={text} className="text-sm text-gray-600 dark:text-gray-300">{text}</p>
          ))}
        </li>
      ))}
    </ol>
  );
}
