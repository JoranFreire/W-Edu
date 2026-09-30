'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { CalendarDaysIcon, ClockIcon } from '@heroicons/react/24/outline';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import { dayLabels, toApiDateTime, toDateTimeLocal } from '@/lib/dates';
import type { User } from '@/types/auth';
import type { InstructorAgenda, InstructorAgendaSuggestion } from '@/types/schedule';

const fieldCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white';
const cardCls = 'rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800';
const TWO_WEEKS_MS = 14 * 24 * 60 * 60 * 1000;

/** Consulta disponibilidade, encontros e horarios livres de um instrutor. */
export default function InstructorAgendaPanel({ instructors, onPickSuggestion }: {
  instructors: User[];
  onPickSuggestion: (suggestion: InstructorAgendaSuggestion) => void;
}) {
  const [form, setForm] = useState(() => ({
    instructor_id: '',
    range_start: toDateTimeLocal(new Date().toISOString()),
    range_end: toDateTimeLocal(new Date(Date.now() + TWO_WEEKS_MS).toISOString()),
    duration_minutes: 60,
  }));
  const [agenda, setAgenda] = useState<InstructorAgenda | null>(null);
  const [loading, setLoading] = useState(false);

  const search = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.instructor_id) {
      setAgenda(null);
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.get<InstructorAgenda>(endpoints.schedule.instructorAgenda(Number(form.instructor_id)), {
        params: {
          range_start: toApiDateTime(form.range_start),
          range_end: toApiDateTime(form.range_end),
          duration_minutes: form.duration_minutes,
        },
      });
      setAgenda(data);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao carregar agenda do instrutor.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Agenda do professor</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Consulte disponibilidade, encontros confirmados e horários livres sugeridos.
        </p>
      </div>
      <form onSubmit={search} className={`grid grid-cols-1 gap-3 md:grid-cols-[1.3fr_1fr_1fr_120px_auto] ${cardCls}`}>
        <select aria-label="Instrutor" value={form.instructor_id} onChange={(e) => setForm((prev) => ({ ...prev, instructor_id: e.target.value }))} className={fieldCls}>
          <option value="">Selecione o instrutor</option>
          {instructors.map((instructor) => <option key={instructor.id} value={instructor.id}>{instructor.name}</option>)}
        </select>
        <input aria-label="Início do período" type="datetime-local" value={form.range_start} onChange={(e) => setForm((prev) => ({ ...prev, range_start: e.target.value }))} className={fieldCls} />
        <input aria-label="Fim do período" type="datetime-local" value={form.range_end} onChange={(e) => setForm((prev) => ({ ...prev, range_end: e.target.value }))} className={fieldCls} />
        <input aria-label="Duração em minutos" type="number" min={15} max={480} step={15} value={form.duration_minutes} onChange={(e) => setForm((prev) => ({ ...prev, duration_minutes: Number(e.target.value) }))} className={fieldCls} />
        <button type="submit" className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-60" disabled={loading || !form.instructor_id}>
          <CalendarDaysIcon className="h-4 w-4" />
          <span>{loading ? 'Carregando' : 'Consultar'}</span>
        </button>
      </form>

      {agenda && (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className={cardCls}>
            <h3 className="font-semibold text-gray-900 dark:text-white">Disponibilidade semanal</h3>
            <div className="mt-3 space-y-2">
              {agenda.availability.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma disponibilidade cadastrada.</p>
              ) : agenda.availability.map((slot) => (
                <div key={slot.id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm dark:bg-gray-900">
                  <span className="text-gray-700 dark:text-gray-300">{dayLabels[slot.day_of_week]}</span>
                  <span className={slot.is_active ? 'text-emerald-700 dark:text-emerald-300' : 'text-gray-400'}>
                    {slot.start_time} - {slot.end_time}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className={cardCls}>
            <h3 className="font-semibold text-gray-900 dark:text-white">Encontros agendados</h3>
            <div className="mt-3 space-y-2">
              {agenda.meetings.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum encontro no período.</p>
              ) : agenda.meetings.map((meeting) => (
                <div key={meeting.id} className="rounded-lg border border-gray-100 p-3 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{meeting.title}</p>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{meeting.course_name} · {meeting.class_name}</p>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {new Date(meeting.starts_at).toLocaleString()} - {new Date(meeting.ends_at).toLocaleTimeString()}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className={cardCls}>
            <h3 className="font-semibold text-gray-900 dark:text-white">Horários sugeridos</h3>
            <div className="mt-3 space-y-2">
              {agenda.suggestions.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Sem horários livres para a duração informada.</p>
              ) : agenda.suggestions.slice(0, 12).map((suggestion) => (
                <button
                  key={`${suggestion.starts_at}-${suggestion.ends_at}`}
                  type="button"
                  onClick={() => onPickSuggestion(suggestion)}
                  className="flex w-full items-center justify-between rounded-lg border border-gray-100 px-3 py-2 text-left text-sm transition-colors hover:border-indigo-200 hover:bg-indigo-50 dark:border-gray-700 dark:hover:border-indigo-700 dark:hover:bg-indigo-950/30"
                >
                  <span className="text-gray-700 dark:text-gray-300">{new Date(suggestion.starts_at).toLocaleString()}</span>
                  <ClockIcon className="h-4 w-4 text-indigo-600" />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
