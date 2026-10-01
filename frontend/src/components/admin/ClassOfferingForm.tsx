'use client';

import { useState } from 'react';
import { AcademicCapIcon, PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import OfferingAcademicFields, { type OfferingAcademicValue } from '@/components/admin/schedule/OfferingAcademicFields';
import { inputCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { toApiDateTime, toDateTimeLocal } from '@/lib/dates';
import { useCreateClassOffering } from '@/lib/hooks/admin/useCreateClassOffering';
import type { User } from '@/types/auth';
import type { Course } from '@/types/course';
import type { ClassOffering, Room } from '@/types/schedule';

const optionalId = (value: string) => value || null;

export default function ClassOfferingForm({ courses, rooms, instructors = [], onCreated, onCancel, variant = 'card' }: {
  courses: Course[];
  rooms: Room[];
  instructors?: User[];
  onCreated: () => void;
  onCancel?: () => void;
  variant?: 'card' | 'plain';
}) {
  const { create } = useCreateClassOffering();
  const [form, setForm] = useState(() => ({
    course_id: '', name: '',
    starts_at: toDateTimeLocal(new Date().toISOString()),
    ends_at: toDateTimeLocal(new Date(Date.now() + 60 * 60 * 1000).toISOString()),
    capacity: 20, status: 'open' as ClassOffering['status'], room_id: '', instructor_id: '',
  }));
  const [academic, setAcademic] = useState<OfferingAcademicValue>({ term_id: '', subject_id: '', class_group_id: '' });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await create({
        course_id: form.course_id, name: form.name,
        starts_at: toApiDateTime(form.starts_at), ends_at: toApiDateTime(form.ends_at),
        capacity: form.capacity, status: form.status,
        room_id: optionalId(form.room_id),
        instructor_id: optionalId(form.instructor_id),
        term_id: optionalId(academic.term_id),
        subject_id: optionalId(academic.subject_id),
        class_group_id: optionalId(academic.class_group_id),
      });
      setForm((p) => ({ ...p, name: '' }));
      toast.success('Turma criada.');
      onCreated();
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao criar turma.'));
    }
  };

  const formCls = variant === 'card'
    ? 'bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-3'
    : 'space-y-4';

  return (
    <form onSubmit={handleSubmit} className={formCls}>
      {variant === 'card' && (
        <div className="flex items-center space-x-2">
          <AcademicCapIcon className="w-5 h-5 text-indigo-600" />
          <h2 className="font-semibold text-gray-900 dark:text-white">Turma</h2>
        </div>
      )}
      <select value={form.course_id} onChange={(e) => setForm((p) => ({ ...p, course_id: e.target.value }))} required className={inputCls}>
        <option value="">Selecione o curso</option>
        {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
      </select>
      <input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} required placeholder="Nome da turma" className={inputCls} />
      <div className="grid grid-cols-2 gap-2">
        <input type="datetime-local" value={form.starts_at} onChange={(e) => setForm((p) => ({ ...p, starts_at: e.target.value }))} className={inputCls} />
        <input type="datetime-local" value={form.ends_at} onChange={(e) => setForm((p) => ({ ...p, ends_at: e.target.value }))} className={inputCls} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <input type="number" min={1} value={form.capacity} onChange={(e) => setForm((p) => ({ ...p, capacity: Number(e.target.value) }))} className={inputCls} />
        <select value={form.room_id} onChange={(e) => setForm((p) => ({ ...p, room_id: e.target.value }))} className={inputCls}>
          <option value="">Sem sala</option>
          {rooms.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
        </select>
      </div>
      <select value={form.instructor_id} onChange={(e) => setForm((p) => ({ ...p, instructor_id: e.target.value }))} className={inputCls}>
        <option value="">Sem instrutor</option>
        {instructors.map((instructor) => <option key={instructor.id} value={instructor.id}>{instructor.name}</option>)}
      </select>
      <OfferingAcademicFields value={academic} onChange={setAcademic} />
      <div className={variant === 'plain' ? 'flex justify-end gap-3 pt-2' : ''}>
        {onCancel && <button type="button" onClick={onCancel} className={secondaryButtonCls}>Cancelar</button>}
        <button className={`${primaryButtonCls} ${variant === 'card' ? 'w-full' : ''}`}>
          <PlusIcon className="w-4 h-4" /><span>Criar turma</span>
        </button>
      </div>
    </form>
  );
}
