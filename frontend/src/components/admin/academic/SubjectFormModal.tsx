'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { fromOptionalInt, toOptionalInt } from '@/lib/forms/numbers';
import type { SubjectInput } from '@/lib/hooks/admin/academic/useSubjects';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { Subject } from '@/types/academic';
import type { Course } from '@/types/course';

export default function SubjectFormModal({ subject, courses, onSave, onClose }: {
  subject?: Subject;
  courses: Course[];
  onSave: (input: SubjectInput) => Promise<void>;
  onClose: () => void;
}) {
  const terms = useTerminology();
  const [form, setForm] = useState({
    code: subject?.code ?? '',
    name: subject?.name ?? '',
    syllabus: subject?.syllabus ?? '',
    hours: String(subject?.hours ?? 0),
    credits: fromOptionalInt(subject?.credits),
    course_id: subject?.course_id ?? null,
    is_active: subject?.is_active ?? true,
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: SubjectInput = {
      ...form,
      syllabus: form.syllabus || null,
      hours: toOptionalInt(form.hours) ?? 0,
      credits: toOptionalInt(form.credits),
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar disciplina.')));
  };

  return (
    <Modal title={subject ? `Editar: ${subject.name}` : terms.newSubject} size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={labelCls}>Código
          <input required value={form.code} onChange={(e) => set({ code: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Nome
          <input required value={form.name} onChange={(e) => set({ name: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Carga horária
          <input type="number" min={0} value={form.hours} onChange={(e) => set({ hours: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Créditos
          <input type="number" min={0} value={form.credits} onChange={(e) => set({ credits: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={`${labelCls} sm:col-span-2`}>Ementa
          <textarea rows={4} value={form.syllabus} onChange={(e) => set({ syllabus: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Conteúdo EAD (curso)
          <select value={form.course_id ?? ''} onChange={(e) => set({ course_id: e.target.value || null })} className={`mt-1 ${inputCls}`}>
            <option value="">Nenhum</option>
            {courses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}
          </select>
        </label>
        <label className="flex items-center gap-2 self-end pb-2 text-sm text-gray-700 dark:text-gray-300">
          <input type="checkbox" checked={form.is_active} onChange={(e) => set({ is_active: e.target.checked })} className="h-4 w-4 rounded border-gray-300" />
          Ativa (pode entrar em novas matrizes)
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
