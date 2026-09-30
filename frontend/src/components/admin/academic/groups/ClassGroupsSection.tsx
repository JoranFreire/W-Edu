'use client';

import { useState } from 'react';
import Link from 'next/link';
import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import SectionHeader from '@/components/common/SectionHeader';
import { dangerIconButtonCls, iconButtonCls, inputCls, sectionCls } from '@/components/common/formStyles';
import { shiftLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { type ClassGroupInput, useClassGroups } from '@/lib/hooks/admin/academic/useClassGroups';
import { usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import { useInstitutionUsers } from '@/lib/hooks/admin/useInstitutionUsers';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { ClassGroup } from '@/types/academicGroups';
import { isAdminRole } from '@/types/auth';
import ClassGroupFormModal from './ClassGroupFormModal';

export default function ClassGroupsSection({ canDelete }: { canDelete: boolean }) {
  const labels = useTerminology();
  const [termId, setTermId] = useState<number | undefined>();
  const { groups, error, save, remove } = useClassGroups(termId);
  const { terms } = useAcademicTerms();
  const { programs } = usePrograms();
  const { users } = useInstitutionUsers();
  const [editing, setEditing] = useState<{ group?: ClassGroup } | null>(null);
  const [toDelete, setToDelete] = useState<ClassGroup | null>(null);
  useErrorToast(error, 'Erro ao carregar turmas.');

  const teachers = users.filter((user) => user.role === 'instructor' || user.role === 'coordinator' || isAdminRole(user.role));
  const termName = (id: number) => terms.find((term) => term.id === id)?.name;
  const programCode = (id: number) => programs.find((program) => program.id === id)?.code;

  const handleSave = async (input: ClassGroupInput) => {
    await save(editing?.group?.id ?? null, input);
    toast.success('Turma salva.');
    setEditing(null);
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await remove(toDelete.id);
      toast.success('Turma excluída.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir turma.'));
    }
    setToDelete(null);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader title="Turmas" description={`Turmas-grupo por ${labels.academicTerm.toLowerCase()}, com turno e professor responsável.`} actionLabel="Nova turma" onAction={() => setEditing({})} />
      <select aria-label={`Filtrar por ${labels.academicTerm.toLowerCase()}`} value={termId ?? ''} onChange={(e) => setTermId(e.target.value ? Number(e.target.value) : undefined)} className={`${inputCls} sm:w-64`}>
        <option value="">Todos os períodos</option>
        {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
      </select>
      {groups.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma turma cadastrada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {groups.map((group) => (
            <li key={group.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div className="min-w-0">
                <Link href={`/admin/academic/class-groups/${group.id}`} className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">{group.name}</Link>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {[programCode(group.program_id), termName(group.term_id), shiftLabels[group.shift]].filter(Boolean).join(' · ')}
                  {' · '}{group.member_count}{group.capacity ? `/${group.capacity}` : ''} alunos
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => setEditing({ group })} aria-label={`Editar turma ${group.name}`} className={iconButtonCls}><PencilSquareIcon className="h-4 w-4" /></button>
                {canDelete && (
                  <button onClick={() => setToDelete(group)} aria-label={`Excluir turma ${group.name}`} className={dangerIconButtonCls}><TrashIcon className="h-4 w-4" /></button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editing && (
        <ClassGroupFormModal group={editing.group} programs={programs} terms={terms} teachers={teachers}
          onSave={handleSave} onClose={() => setEditing(null)} />
      )}
      {toDelete && (
        <ConfirmDialog title="Excluir turma" message={`Excluir a turma "${toDelete.name}"?`} confirmLabel="Excluir" danger
          onCancel={() => setToDelete(null)} onConfirm={handleDelete} />
      )}
    </section>
  );
}
