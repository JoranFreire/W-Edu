'use client';

import { useState } from 'react';
import { LinkIcon, PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import SectionHeader from '@/components/common/SectionHeader';
import StatusBadge from '@/components/common/StatusBadge';
import { dangerIconButtonCls, iconButtonCls, inputCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { type SubjectInput, useSubjects } from '@/lib/hooks/admin/academic/useSubjects';
import { useCourses } from '@/lib/hooks/admin/useCourses';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { Subject } from '@/types/academic';
import SubjectFormModal from './SubjectFormModal';
import SubjectLinksModal from './SubjectLinksModal';

export default function SubjectsSection({ canDelete }: { canDelete: boolean }) {
  const terms = useTerminology();
  const { subjects, error, save, remove } = useSubjects();
  const { courses } = useCourses();
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState<{ subject?: Subject } | null>(null);
  const [linking, setLinking] = useState<Subject | null>(null);
  const [toDelete, setToDelete] = useState<Subject | null>(null);
  useErrorToast(error, 'Erro ao carregar disciplinas.');

  const term = search.trim().toLowerCase();
  const visible = term ? subjects.filter((s) => `${s.code} ${s.name}`.toLowerCase().includes(term)) : subjects;

  const handleSave = async (input: SubjectInput) => {
    await save(editing?.subject?.id ?? null, input);
    toast.success('Disciplina salva.');
    setEditing(null);
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await remove(toDelete);
      toast.success('Disciplina excluída.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir disciplina.'));
    }
    setToDelete(null);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader
        title={terms.subjects}
        description="Ementa, carga horária, créditos, pré-requisitos e equivalências."
        actionLabel={terms.newSubject}
        onAction={() => setEditing({})}
      />
      <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por código ou nome" aria-label="Buscar disciplinas" className={inputCls} />
      {visible.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma disciplina encontrada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {visible.map((subject) => (
            <li key={subject.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div className="min-w-0">
                <p className="font-medium text-gray-900 dark:text-white">{subject.code} · {subject.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {subject.hours}h{subject.credits !== null ? ` · ${subject.credits} créditos` : ''}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <StatusBadge active={subject.is_active} />
                <button onClick={() => setLinking(subject)} aria-label={`Vínculos de ${subject.code}`} className={iconButtonCls}>
                  <LinkIcon className="h-4 w-4" />
                </button>
                <button onClick={() => setEditing({ subject })} aria-label={`Editar ${subject.code}`} className={iconButtonCls}>
                  <PencilSquareIcon className="h-4 w-4" />
                </button>
                {canDelete && (
                  <button onClick={() => setToDelete(subject)} aria-label={`Excluir ${subject.code}`} className={dangerIconButtonCls}>
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editing && <SubjectFormModal subject={editing.subject} courses={courses} onSave={handleSave} onClose={() => setEditing(null)} />}
      {linking && <SubjectLinksModal subject={linking} subjects={subjects} canRemove={canDelete} onClose={() => setLinking(null)} />}
      {toDelete && (
        <ConfirmDialog title="Excluir disciplina" message={`Excluir "${toDelete.name}"?`} confirmLabel="Excluir" danger
          onCancel={() => setToDelete(null)} onConfirm={handleDelete} />
      )}
    </section>
  );
}
