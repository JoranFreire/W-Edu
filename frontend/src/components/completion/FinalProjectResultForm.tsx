'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { FinalProject, FinalProjectResultInput } from '@/types/completion';

/** Orientador registra a entrega e, depois, o resultado da defesa. */
export default function FinalProjectResultForm({ project, onRecord }: {
  project: FinalProject;
  onRecord: (input: FinalProjectResultInput) => Promise<void>;
}) {
  const [defense, setDefense] = useState({ on: todayIso(), grade: '', committee: '' });
  const record = async (status: FinalProjectResultInput['status']) => {
    const input: FinalProjectResultInput = status === 'submitted'
      ? { status, defense_on: null, grade: null, committee: null }
      : { status, defense_on: defense.on, grade: defense.grade === '' ? null : Number(defense.grade), committee: defense.committee || null };
    try {
      await onRecord(input);
      toast.success(status === 'submitted' ? 'Entrega registrada.' : 'Resultado registrado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar.'));
    }
  };

  if (project.status === 'in_progress') {
    return <button onClick={() => record('submitted')} aria-label={`Registrar entrega de ${project.title}`} className={secondaryButtonCls}>Registrar entrega</button>;
  }
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
      <input type="date" aria-label="Data da defesa" value={defense.on} onChange={(e) => setDefense({ ...defense, on: e.target.value })} className={inputCls} />
      <input type="number" min={0} step="0.1" aria-label="Nota do TCC" value={defense.grade} onChange={(e) => setDefense({ ...defense, grade: e.target.value })} placeholder="Nota" className={inputCls} />
      <input aria-label="Banca" value={defense.committee} onChange={(e) => setDefense({ ...defense, committee: e.target.value })} placeholder="Banca" className={inputCls} />
      <button onClick={() => record('approved')} aria-label={`Aprovar ${project.title}`} className={primaryButtonCls}>Aprovar</button>
      <button onClick={() => record('failed')} aria-label={`Reprovar ${project.title}`} className={secondaryButtonCls}>Reprovar</button>
    </div>
  );
}
