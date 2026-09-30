'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { optionsOf, shiftLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { fromOptionalInt, toOptionalInt } from '@/lib/forms/numbers';
import type { ClassGroupInput } from '@/lib/hooks/admin/academic/useClassGroups';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { Program } from '@/types/academic';
import type { AcademicTerm } from '@/types/academicCalendar';
import type { ClassGroup, Shift } from '@/types/academicGroups';
import type { User } from '@/types/auth';

export default function ClassGroupFormModal({ group, programs, terms, teachers, onSave, onClose }: {
  group?: ClassGroup;
  programs: Program[];
  terms: AcademicTerm[];
  teachers: User[];
  onSave: (input: ClassGroupInput) => Promise<void>;
  onClose: () => void;
}) {
  const labels = useTerminology();
  const [form, setForm] = useState({
    program_id: String(group?.program_id ?? ''),
    term_id: String(group?.term_id ?? ''),
    name: group?.name ?? '',
    curriculum_term_number: fromOptionalInt(group?.curriculum_term_number),
    shift: group?.shift ?? ('morning' as Shift),
    capacity: fromOptionalInt(group?.capacity),
    homeroom_teacher_id: String(group?.homeroom_teacher_id ?? ''),
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: ClassGroupInput = {
      program_id: Number(form.program_id),
      term_id: Number(form.term_id),
      name: form.name,
      curriculum_term_number: toOptionalInt(form.curriculum_term_number),
      shift: form.shift,
      capacity: toOptionalInt(form.capacity),
      homeroom_teacher_id: form.homeroom_teacher_id ? Number(form.homeroom_teacher_id) : null,
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar turma.')));
  };

  return (
    <Modal title={group ? `Editar turma ${group.name}` : 'Nova turma'} size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={labelCls}>{labels.program}
          <select required disabled={!!group} value={form.program_id} onChange={(e) => set({ program_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione...</option>
            {programs.map((program) => <option key={program.id} value={program.id}>{program.code} · {program.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>{labels.academicTerm}
          <select required disabled={!!group} value={form.term_id} onChange={(e) => set({ term_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione...</option>
            {terms.filter((term) => term.status !== 'closed' || term.id === group?.term_id).map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Nome
          <input required value={form.name} onChange={(e) => set({ name: e.target.value })} placeholder="Ex.: 7º ano A" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>{labels.term} da matriz
          <input type="number" min={1} value={form.curriculum_term_number} onChange={(e) => set({ curriculum_term_number: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Turno
          <select value={form.shift} onChange={(e) => set({ shift: e.target.value as Shift })} className={`mt-1 ${inputCls}`}>
            {optionsOf(shiftLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Vagas
          <input type="number" min={1} value={form.capacity} onChange={(e) => set({ capacity: e.target.value })} placeholder="Sem limite" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={`${labelCls} sm:col-span-2`}>Professor responsável
          <select value={form.homeroom_teacher_id} onChange={(e) => set({ homeroom_teacher_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Nenhum</option>
            {teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.name}</option>)}
          </select>
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
