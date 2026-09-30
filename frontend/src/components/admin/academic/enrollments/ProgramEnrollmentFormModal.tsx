'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { ProgramEnrollmentInput } from '@/lib/hooks/admin/academic/useProgramEnrollments';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { Program } from '@/types/academic';
import type { AcademicTerm } from '@/types/academicCalendar';
import type { PersonSummary } from '@/types/academicGroups';

/** Nova matricula: aluno, programa, periodo de ingresso e numero opcional (senao gerado). */
export default function ProgramEnrollmentFormModal({ students, programs, terms, onSave, onClose }: {
  students: PersonSummary[];
  programs: Program[];
  terms: AcademicTerm[];
  onSave: (input: ProgramEnrollmentInput) => Promise<void>;
  onClose: () => void;
}) {
  const labels = useTerminology();
  const [form, setForm] = useState({ student_id: '', program_id: '', entry_term_id: '', registration_number: '' });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: ProgramEnrollmentInput = {
      student_id: Number(form.student_id),
      program_id: Number(form.program_id),
      entry_term_id: form.entry_term_id ? Number(form.entry_term_id) : null,
      registration_number: form.registration_number.trim() || null,
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao matricular.')));
  };

  return (
    <Modal title="Nova matrícula" description="A matrícula usa a matriz vigente do programa." size="md" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <label className={labelCls}>Aluno
          <select required value={form.student_id} onChange={(e) => set({ student_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione...</option>
            {students.map((student) => <option key={student.id} value={student.id}>{student.name} ({student.email})</option>)}
          </select>
        </label>
        <label className={labelCls}>{labels.program}
          <select required value={form.program_id} onChange={(e) => set({ program_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione...</option>
            {programs.map((program) => <option key={program.id} value={program.id}>{program.code} · {program.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Ingresso ({labels.academicTerm.toLowerCase()})
          <select value={form.entry_term_id} onChange={(e) => set({ entry_term_id: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Não informado</option>
            {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Número de matrícula (opcional)
          <input value={form.registration_number} onChange={(e) => set({ registration_number: e.target.value })} placeholder="Gerado automaticamente" className={`mt-1 ${inputCls}`} />
        </label>
        <FormActions saving={saving} onCancel={onClose} submitLabel="Matricular" />
      </form>
    </Modal>
  );
}
