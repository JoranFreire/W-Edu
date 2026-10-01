import type { OfferingSituation, TimeSlot } from '@/types/registration';

/** Dia da semana da API (0 = segunda). */
export const weekdayLabels = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];

export const situationLabels: Record<OfferingSituation, string> = {
  enrolled: 'Inscrito',
  waitlisted: 'Lista de espera',
  available: 'Disponível',
  full: 'Lotada',
  blocked: 'Indisponível',
};

export const situationCls: Record<OfferingSituation, string> = {
  enrolled: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  waitlisted: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  available: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300',
  full: 'bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300',
  blocked: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

/** "Segunda 08:00–10:00". */
export function formatSlot(slot: Pick<TimeSlot, 'weekday' | 'starts_at' | 'ends_at'>): string {
  return `${weekdayLabels[slot.weekday]} ${slot.starts_at.slice(0, 5)}–${slot.ends_at.slice(0, 5)}`;
}
