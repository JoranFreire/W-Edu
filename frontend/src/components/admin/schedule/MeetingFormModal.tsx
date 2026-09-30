'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import Modal from '@/components/common/Modal';
import { apiErrorMessage } from '@/lib/api/errors';
import { toApiDateTime, toDateTimeLocal } from '@/lib/dates';
import type { MeetingDraft } from '@/lib/hooks/admin/useClassMeetings';
import type { ClassOffering, MeetingType, Room } from '@/types/schedule';

const fieldCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white';

export interface MeetingSlot {
  starts_at: string;
  ends_at: string;
}

/** Formulario de novo encontro de uma turma, opcionalmente num horario sugerido. */
export default function MeetingFormModal({ classOffering, rooms, slot, onSubmit, onClose }: {
  classOffering: ClassOffering;
  rooms: Room[];
  slot: MeetingSlot | null;
  onSubmit: (draft: MeetingDraft) => Promise<unknown>;
  onClose: () => void;
}) {
  const [form, setForm] = useState(() => ({
    title: '',
    room_id: classOffering.room_id ? String(classOffering.room_id) : '',
    starts_at: slot?.starts_at ?? toDateTimeLocal(classOffering.starts_at),
    ends_at: slot?.ends_at ?? toDateTimeLocal(classOffering.ends_at),
    type: (classOffering.room_id ? 'in_person' : 'live') as MeetingType,
  }));

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSubmit({
        class_offering_id: classOffering.id,
        room_id: form.room_id ? Number(form.room_id) : null,
        title: form.title,
        starts_at: toApiDateTime(form.starts_at),
        ends_at: toApiDateTime(form.ends_at),
        type: form.type,
      });
      toast.success('Encontro criado.');
      onClose();
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao criar encontro.'));
    }
  };

  return (
    <Modal title="Criar encontro" description={classOffering.name} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input value={form.title} onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))} required placeholder="Título do encontro" className={fieldCls} />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <input aria-label="Início" type="datetime-local" value={form.starts_at} onChange={(e) => setForm((prev) => ({ ...prev, starts_at: e.target.value }))} required className={fieldCls} />
          <input aria-label="Fim" type="datetime-local" value={form.ends_at} onChange={(e) => setForm((prev) => ({ ...prev, ends_at: e.target.value }))} required className={fieldCls} />
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <select aria-label="Tipo" value={form.type} onChange={(e) => setForm((prev) => ({ ...prev, type: e.target.value as MeetingType }))} className={fieldCls}>
            <option value="live">Live</option>
            <option value="in_person">Presencial</option>
            <option value="hybrid">Híbrido</option>
          </select>
          <select aria-label="Sala" value={form.room_id} onChange={(e) => setForm((prev) => ({ ...prev, room_id: e.target.value }))} className={fieldCls}>
            <option value="">Sem sala</option>
            {rooms.map((room) => <option key={room.id} value={room.id}>{room.name}</option>)}
          </select>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
            Cancelar
          </button>
          <button className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">Criar encontro</button>
        </div>
      </form>
    </Modal>
  );
}
