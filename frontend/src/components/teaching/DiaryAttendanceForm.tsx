'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import { inputCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { DiaryAttendanceInput } from '@/lib/hooks/teaching/useDiaryAttendance';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { DiaryAttendanceRow } from '@/types/assessment';

/** Chamada editavel: faltas por aluno (0 ate o numero de aulas) e justificativa. */
export default function DiaryAttendanceForm({ rows, lessonCount, readOnly, onSave, onClose }: {
  rows: DiaryAttendanceRow[];
  lessonCount: number;
  readOnly: boolean;
  onSave: (rows: DiaryAttendanceInput[]) => Promise<void>;
  onClose: () => void;
}) {
  const [values, setValues] = useState<DiaryAttendanceInput[]>(() =>
    rows.map(({ class_enrollment_id, absences, justified, note }) => ({ class_enrollment_id, absences, justified, note })),
  );
  const { saving, run } = useSubmitting();
  const update = (index: number, patch: Partial<DiaryAttendanceInput>) =>
    setValues(values.map((value, i) => (i === index ? { ...value, ...patch } : value)));

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(async () => {
      await onSave(values);
      toast.success('Chamada salva.');
      onClose();
    }).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar chamada.')));
  };

  if (rows.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno inscrito na turma.</p>;
  return (
    <form onSubmit={submit} className="space-y-3">
      <ul className="divide-y divide-gray-200 dark:divide-gray-700">
        {rows.map((row, index) => (
          <li key={row.class_enrollment_id} className="flex flex-wrap items-center justify-between gap-3 py-2">
            <span className="text-sm text-gray-900 dark:text-white">{row.student.name}</span>
            <div className="flex items-center gap-3">
              <select
                disabled={readOnly}
                aria-label={`Faltas de ${row.student.name}`}
                value={values[index].absences}
                onChange={(e) => update(index, { absences: Number(e.target.value) })}
                className={`${inputCls} w-36`}
              >
                {Array.from({ length: lessonCount + 1 }, (_, n) => (
                  <option key={n} value={n}>{n === 0 ? 'Presente' : `${n} falta${n > 1 ? 's' : ''}`}</option>
                ))}
              </select>
              <label className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300">
                <input type="checkbox" disabled={readOnly || values[index].absences === 0} checked={values[index].justified}
                  onChange={(e) => update(index, { justified: e.target.checked })} className="h-4 w-4 rounded border-gray-300" />
                Justificada
              </label>
            </div>
          </li>
        ))}
      </ul>
      {!readOnly && <FormActions saving={saving} onCancel={onClose} submitLabel="Salvar chamada" />}
    </form>
  );
}
