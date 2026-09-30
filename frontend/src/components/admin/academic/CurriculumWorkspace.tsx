'use client';

import { useState } from 'react';
import { ClipboardDocumentListIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import { primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { type CurriculumInput, useCurricula } from '@/lib/hooks/admin/academic/useCurricula';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Curriculum } from '@/types/academic';
import CurriculumEditor from './CurriculumEditor';
import CurriculumVersionBar from './CurriculumVersionBar';
import CurriculumVersionModal from './CurriculumVersionModal';

function defaultCurriculum(curricula: Curriculum[]): Curriculum | undefined {
  return curricula.find((curriculum) => curriculum.status === 'active') ?? curricula[curricula.length - 1];
}

/** Versoes da matriz de um programa: escolha da versao e ciclo de vida. */
export default function CurriculumWorkspace({ programId, canDelete }: { programId: number; canDelete: boolean }) {
  const { curricula, error, create, newVersion, activate, archive, remove } = useCurricula(programId);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [creating, setCreating] = useState<'empty' | 'copy' | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  useErrorToast(error, 'Erro ao carregar matrizes.');

  const selected = curricula.find((curriculum) => curriculum.id === selectedId) ?? defaultCurriculum(curricula);

  const act = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir a ação.'));
    }
  };

  const handleCreate = async (input: CurriculumInput) => {
    const created = creating === 'copy' && selected ? await newVersion(selected.id, input) : await create(input);
    setSelectedId(created.id);
    setCreating(null);
    toast.success('Matriz criada em rascunho.');
  };

  const handleDelete = async () => {
    if (!selected) return;
    await act(() => remove(selected.id), 'Rascunho excluído.');
    setSelectedId(null);
    setConfirmDelete(false);
  };

  return (
    <section className={`${sectionCls} space-y-5`}>
      <div className="flex items-center gap-3">
        <ClipboardDocumentListIcon className="h-5 w-5 text-indigo-600" />
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Matriz curricular</h2>
      </div>
      {!selected ? (
        <div className="space-y-3 text-sm text-gray-500 dark:text-gray-400">
          <p>Este programa ainda não tem matriz curricular.</p>
          <button onClick={() => setCreating('empty')} className={primaryButtonCls}>Criar matriz</button>
        </div>
      ) : (
        <>
          <CurriculumVersionBar
            curricula={curricula}
            selected={selected}
            canDelete={canDelete}
            onSelect={setSelectedId}
            onActivate={() => act(() => activate(selected.id), 'Matriz vigente atualizada.')}
            onArchive={() => act(() => archive(selected.id), 'Matriz arquivada.')}
            onNewVersion={() => setCreating('copy')}
            onDelete={() => setConfirmDelete(true)}
          />
          <CurriculumEditor key={`${selected.id}-${selected.status}`} curriculumId={selected.id} />
        </>
      )}
      {creating && (
        <CurriculumVersionModal sourceVersion={creating === 'copy' ? selected?.version : undefined}
          onSave={handleCreate} onClose={() => setCreating(null)} />
      )}
      {confirmDelete && selected && (
        <ConfirmDialog title="Excluir rascunho" message={`Excluir a versão ${selected.version}?`} confirmLabel="Excluir" danger
          onCancel={() => setConfirmDelete(false)} onConfirm={handleDelete} />
      )}
    </section>
  );
}
