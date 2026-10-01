'use client';

import { useState } from 'react';
import { TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { ClassGroupMember, ProgramEnrollment } from '@/types/academicGroups';

/** Alunos da turma e alocacao de matriculas ativas do programa. */
export default function ClassGroupRoster({ members, candidates, onAdd, onRemove }: {
  members: ClassGroupMember[];
  candidates: ProgramEnrollment[];
  onAdd: (enrollmentId: string) => Promise<void>;
  onRemove: (enrollmentId: string) => Promise<void>;
}) {
  const [selected, setSelected] = useState('');

  const attempt = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir a ação.'));
    }
  };

  const handleAdd = (event: React.FormEvent) => {
    event.preventDefault();
    if (!selected) return;
    attempt(async () => {
      await onAdd(selected);
      setSelected('');
    }, 'Aluno incluído na turma.');
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Alunos ({members.length})</h2>
      {members.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno na turma.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {members.map((member) => (
            <li key={member.id} className="flex items-center justify-between gap-3 py-2">
              <p className="text-sm text-gray-900 dark:text-white">
                <span className="font-mono text-gray-500 dark:text-gray-400">{member.registration_number}</span> · {member.student.name}
              </p>
              <button onClick={() => attempt(() => onRemove(member.program_enrollment_id), 'Aluno removido da turma.')}
                aria-label={`Remover ${member.student.name}`} className={dangerIconButtonCls}>
                <TrashIcon className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={handleAdd} className="flex flex-col gap-3 sm:flex-row">
        <select aria-label="Aluno para incluir" value={selected} onChange={(e) => setSelected(e.target.value)} className={inputCls}>
          <option value="">Selecione uma matrícula ativa...</option>
          {candidates.map((enrollment) => (
            <option key={enrollment.id} value={enrollment.id}>{enrollment.registration_number} · {enrollment.student.name}</option>
          ))}
        </select>
        <button disabled={!selected} className={primaryButtonCls}>Incluir</button>
      </form>
    </section>
  );
}
