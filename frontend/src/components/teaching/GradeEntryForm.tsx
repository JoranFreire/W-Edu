'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import { inputCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { GradeInput } from '@/lib/hooks/teaching/useGrades';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { GradeRow } from '@/types/assessment';

/** Tabela editavel de notas; o estado parte das notas carregadas (monte com `key`). */
export default function GradeEntryForm({ rows, maxScore, onSave, onClose }: {
  rows: GradeRow[];
  maxScore: number;
  onSave: (grades: GradeInput[]) => Promise<void>;
  onClose: () => void;
}) {
  const [scores, setScores] = useState(() => Object.fromEntries(rows.map((row) => [row.class_enrollment_id, row.score === null ? '' : String(row.score)])));
  const { saving, run } = useSubmitting();

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const grades = rows.map((row) => {
      const text = scores[row.class_enrollment_id]?.replace(',', '.').trim() ?? '';
      return { class_enrollment_id: row.class_enrollment_id, score: text === '' ? null : Number(text), notes: row.notes };
    });
    run(async () => {
      await onSave(grades);
      toast.success('Notas salvas.');
      onClose();
    }).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar notas.')));
  };

  if (rows.length === 0) return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno inscrito na turma.</p>;
  return (
    <form onSubmit={submit} className="space-y-3">
      <ul className="divide-y divide-gray-200 dark:divide-gray-700">
        {rows.map((row) => (
          <li key={row.class_enrollment_id} className="flex items-center justify-between gap-3 py-2">
            <span className="text-sm text-gray-900 dark:text-white">{row.student.name}</span>
            <input
              inputMode="decimal"
              aria-label={`Nota de ${row.student.name}`}
              value={scores[row.class_enrollment_id] ?? ''}
              onChange={(e) => setScores({ ...scores, [row.class_enrollment_id]: e.target.value })}
              placeholder={`0 a ${maxScore}`}
              className={`${inputCls} w-28 text-right`}
            />
          </li>
        ))}
      </ul>
      <FormActions saving={saving} onCancel={onClose} submitLabel="Salvar notas" />
    </form>
  );
}
