'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { RecoveryInput } from '@/lib/hooks/teaching/useOfferingResults';
import type { FinalResultRow } from '@/types/assessment';

/** Notas de recuperacao dos alunos abaixo da media (monte com `key` a partir das linhas carregadas). */
export default function RecoveryForm({ rows, maxScore, onSave }: {
  rows: FinalResultRow[];
  maxScore: number;
  onSave: (values: RecoveryInput[]) => Promise<void>;
}) {
  const [scores, setScores] = useState(() => Object.fromEntries(rows.map((row) => [row.class_enrollment_id, row.recovery_score === null ? '' : String(row.recovery_score)])));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const values = rows.map((row) => {
      const text = scores[row.class_enrollment_id]?.replace(',', '.').trim() ?? '';
      return { class_enrollment_id: row.class_enrollment_id, score: text === '' ? null : Number(text) };
    });
    try {
      await onSave(values);
      toast.success('Recuperação salva.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar recuperação.'));
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3 rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/10">
      <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-200">Recuperação (substitui a média quando maior)</h3>
      <ul className="space-y-2">
        {rows.map((row) => (
          <li key={row.class_enrollment_id} className="flex items-center justify-between gap-3">
            <span className="text-sm text-gray-900 dark:text-white">{row.student.name}</span>
            <input
              inputMode="decimal"
              aria-label={`Recuperação de ${row.student.name}`}
              value={scores[row.class_enrollment_id] ?? ''}
              onChange={(e) => setScores({ ...scores, [row.class_enrollment_id]: e.target.value })}
              placeholder={`0 a ${maxScore}`}
              className={`${inputCls} w-28 text-right`}
            />
          </li>
        ))}
      </ul>
      <button className={primaryButtonCls}>Salvar recuperação</button>
    </form>
  );
}
