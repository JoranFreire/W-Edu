'use client';

import { useState } from 'react';
import { TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { calendarEventKindLabels, optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { type CalendarEventInput, useTermCalendar } from '@/lib/hooks/admin/academic/useTermCalendar';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { CalendarEventKind } from '@/types/academicCalendar';

const emptyDraft: CalendarEventInput = { kind: 'holiday', title: '', starts_on: '', ends_on: null };

/** Calendario do periodo: dias letivos calculados e eventos (feriados, recessos, provas). */
export default function CalendarPanel({ termId, editable }: { termId: number; editable: boolean }) {
  const { events, summary, error, add, remove } = useTermCalendar(termId);
  const [draft, setDraft] = useState(emptyDraft);
  useErrorToast(error, 'Erro ao carregar calendário.');

  const handleAdd = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await add(draft);
      setDraft(emptyDraft);
      toast.success('Evento adicionado.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao adicionar evento.'));
    }
  };

  const handleRemove = async (id: number) => {
    try { await remove(id); } catch (err) { toast.error(apiErrorMessage(err, 'Erro ao remover evento.')); }
  };

  const stats = summary ? [
    { label: 'Dias letivos', value: summary.school_days },
    { label: 'Feriados e recessos (dias úteis)', value: summary.non_school_days },
    { label: 'Dias letivos extras', value: summary.extra_school_days },
    { label: 'Avaliações', value: summary.exams },
  ] : [];

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Calendário acadêmico</h2>
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
            <dt className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</dt>
            <dd className="text-lg font-semibold text-gray-900 dark:text-white">{stat.value}</dd>
          </div>
        ))}
      </dl>
      {events.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum evento no calendário.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {events.map((item) => (
            <li key={item.id} className="flex items-center justify-between gap-3 py-2">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{item.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {calendarEventKindLabels[item.kind]} · {formatIsoDate(item.starts_on)}{item.ends_on ? ` a ${formatIsoDate(item.ends_on)}` : ''}
                </p>
              </div>
              {editable && (
                <button onClick={() => handleRemove(item.id)} aria-label={`Remover evento ${item.title}`} className={dangerIconButtonCls}>
                  <TrashIcon className="h-4 w-4" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      {editable && (
        <form onSubmit={handleAdd} className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1.5fr_1fr_1fr_auto]">
          <select aria-label="Tipo de evento" value={draft.kind} onChange={(e) => setDraft({ ...draft, kind: e.target.value as CalendarEventKind })} className={inputCls}>
            {optionsOf(calendarEventKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
          <input required aria-label="Título do evento" value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} placeholder="Título" className={inputCls} />
          <input required type="date" aria-label="Data do evento" value={draft.starts_on} onChange={(e) => setDraft({ ...draft, starts_on: e.target.value })} className={inputCls} />
          <input type="date" aria-label="Até (opcional)" value={draft.ends_on ?? ''} onChange={(e) => setDraft({ ...draft, ends_on: e.target.value || null })} className={inputCls} />
          <button className={primaryButtonCls}>Adicionar</button>
        </form>
      )}
    </section>
  );
}
