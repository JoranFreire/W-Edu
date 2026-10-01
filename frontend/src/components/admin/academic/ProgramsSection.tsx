'use client';

import { useState } from 'react';
import Link from 'next/link';
import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import SectionHeader from '@/components/common/SectionHeader';
import StatusBadge from '@/components/common/StatusBadge';
import { dangerIconButtonCls, iconButtonCls, sectionCls } from '@/components/common/formStyles';
import { programLevelLabels, programStatusLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAcademicUnits } from '@/lib/hooks/admin/academic/useAcademicUnits';
import { type ProgramInput, usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { Program } from '@/types/academic';
import ProgramFormModal from './ProgramFormModal';

export default function ProgramsSection({ canDelete }: { canDelete: boolean }) {
  const terms = useTerminology();
  const { programs, error, save, remove } = usePrograms();
  const { units } = useAcademicUnits();
  const [editing, setEditing] = useState<{ program?: Program } | null>(null);
  const [toDelete, setToDelete] = useState<Program | null>(null);
  useErrorToast(error, 'Erro ao carregar programas.');
  const unitName = (id: string | null) => units.find((unit) => unit.id === id)?.name;

  const handleSave = async (input: ProgramInput) => {
    await save(editing?.program?.id ?? null, input);
    toast.success('Programa salvo.');
    setEditing(null);
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await remove(toDelete);
      toast.success('Programa excluído.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir programa.'));
    }
    setToDelete(null);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader
        title={terms.programs}
        description="Cada programa tem matrizes curriculares versionadas."
        actionLabel={terms.newProgram}
        onAction={() => setEditing({})}
      />
      {programs.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum programa cadastrado.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {programs.map((program) => (
            <li key={program.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div className="min-w-0">
                <Link href={`/admin/academic/programs/${program.id}`} className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
                  {program.code} · {program.name}
                </Link>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {[programLevelLabels[program.level], unitName(program.unit_id), program.duration_terms && `${program.duration_terms} ${terms.term.toLowerCase()}s`]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge active={program.status === 'active'} activeLabel={programStatusLabels.active} inactiveLabel={programStatusLabels[program.status]} />
                <button onClick={() => setEditing({ program })} aria-label={`Editar programa ${program.code}`} className={iconButtonCls}>
                  <PencilSquareIcon className="h-4 w-4" />
                </button>
                {canDelete && (
                  <button onClick={() => setToDelete(program)} aria-label={`Excluir programa ${program.code}`} className={dangerIconButtonCls}>
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editing && <ProgramFormModal program={editing.program} units={units} onSave={handleSave} onClose={() => setEditing(null)} />}
      {toDelete && (
        <ConfirmDialog title="Excluir programa" message={`Excluir "${toDelete.name}"?`} confirmLabel="Excluir" danger
          onCancel={() => setToDelete(null)} onConfirm={handleDelete} />
      )}
    </section>
  );
}
