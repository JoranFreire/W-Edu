'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { TrashIcon } from '@heroicons/react/24/outline';
import Modal from '@/components/common/Modal';
import { dangerIconButtonCls, inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { formatSlot, weekdayLabels } from '@/lib/academic/registrationLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useOfferingTimeSlots } from '@/lib/hooks/registration/useOfferingTimeSlots';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { TimeSlotInput } from '@/types/registration';

const emptySlot: TimeSlotInput = { weekday: 0, starts_at: '08:00', ends_at: '10:00' };

/** Horario semanal da oferta de disciplina (base do choque de horario na matricula). */
export default function OfferingTimeSlotsModal({ offeringId, offeringName, onClose }: {
  offeringId: number;
  offeringName: string;
  onClose: () => void;
}) {
  const { slots, error, add, remove } = useOfferingTimeSlots(offeringId);
  const [draft, setDraft] = useState(emptySlot);
  useErrorToast(error, 'Erro ao carregar os horários.');

  const run = async (action: () => Promise<void>, fallback: string) => {
    try {
      await action();
    } catch (err) {
      toast.error(apiErrorMessage(err, fallback));
    }
  };
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => add(draft), 'Erro ao adicionar horário.');
  };

  return (
    <Modal title={`Horários: ${offeringName}`} description="Usados para impedir choque de horário na matrícula por disciplina." onClose={onClose}>
      <div className="space-y-4">
        {slots.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum horário cadastrado.</p> : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {slots.map((slot) => (
              <li key={slot.id} className="flex items-center justify-between py-2 text-sm text-gray-800 dark:text-gray-200">
                {formatSlot(slot)}
                <button onClick={() => run(() => remove(slot.id), 'Erro ao remover horário.')} aria-label={`Remover ${formatSlot(slot)}`} className={dangerIconButtonCls}>
                  <TrashIcon className="h-4 w-4" />
                </button>
              </li>
            ))}
          </ul>
        )}
        <form onSubmit={submit} className="grid grid-cols-1 gap-3 sm:grid-cols-4">
          <select aria-label="Dia da semana" value={draft.weekday} onChange={(e) => setDraft({ ...draft, weekday: Number(e.target.value) })} className={inputCls}>
            {weekdayLabels.map((label, index) => <option key={label} value={index}>{label}</option>)}
          </select>
          <input type="time" required aria-label="Início" value={draft.starts_at} onChange={(e) => setDraft({ ...draft, starts_at: e.target.value })} className={inputCls} />
          <input type="time" required aria-label="Fim" value={draft.ends_at} onChange={(e) => setDraft({ ...draft, ends_at: e.target.value })} className={inputCls} />
          <button className={primaryButtonCls}>Adicionar</button>
        </form>
      </div>
    </Modal>
  );
}
