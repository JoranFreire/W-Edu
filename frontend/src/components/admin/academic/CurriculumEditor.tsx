'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import SectionHeader from '@/components/common/SectionHeader';
import Spinner from '@/components/common/Spinner';
import { apiErrorMessage } from '@/lib/api/errors';
import { type ComponentInput, useCurriculumDetail } from '@/lib/hooks/admin/academic/useCurriculumDetail';
import { useSubjects } from '@/lib/hooks/admin/academic/useSubjects';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { CurriculumComponent } from '@/types/academic';
import ComponentFormModal from './ComponentFormModal';
import CurriculumBoard from './CurriculumBoard';
import CurriculumSummary from './CurriculumSummary';

/** Conteudo de uma versao da matriz: totais, pendencias e componentes por periodo. */
export default function CurriculumEditor({ curriculumId }: { curriculumId: string }) {
  const terms = useTerminology();
  const { detail, error, addComponent, updateComponent, removeComponent } = useCurriculumDetail(curriculumId);
  const { subjects } = useSubjects();
  const [editing, setEditing] = useState<{ component?: CurriculumComponent } | null>(null);
  const [toRemove, setToRemove] = useState<CurriculumComponent | null>(null);
  useErrorToast(error, 'Erro ao carregar matriz.');

  if (!detail) return <Spinner variant="panel" />;
  const editable = detail.status === 'draft';
  const usedIds = new Set(detail.components.map((component) => component.subject.id));
  const available = subjects.filter((subject) => subject.is_active && !usedIds.has(subject.id));

  const handleSave = async ({ subject_id: subjectId, ...fields }: ComponentInput) => {
    if (editing?.component) await updateComponent(editing.component.id, fields);
    else await addComponent({ subject_id: subjectId, ...fields });
    toast.success('Matriz atualizada.');
    setEditing(null);
  };

  const handleRemove = async () => {
    if (!toRemove) return;
    try { await removeComponent(toRemove.id); } catch (err) { toast.error(apiErrorMessage(err, 'Erro ao remover componente.')); }
    setToRemove(null);
  };

  return (
    <div className="space-y-5">
      <CurriculumSummary detail={detail} termLabel={terms.term} />
      <SectionHeader
        title="Componentes"
        description={editable ? undefined : 'Matriz vigente ou arquivada é somente leitura; crie uma nova versão para alterar.'}
        actionLabel={editable ? `Incluir ${terms.subject.toLowerCase()}` : undefined}
        onAction={editable ? () => setEditing({}) : undefined}
      />
      <CurriculumBoard components={detail.components} termLabel={terms.term} editable={editable}
        onEdit={(component) => setEditing({ component })} onRemove={setToRemove} />
      {editing && (
        <ComponentFormModal component={editing.component} subjects={available} termLabel={terms.term}
          defaultTerm={Math.max(1, detail.totals.terms)} onSave={handleSave} onClose={() => setEditing(null)} />
      )}
      {toRemove && (
        <ConfirmDialog title="Remover componente" message={`Remover ${toRemove.subject.code} da matriz?`} confirmLabel="Remover" danger
          onCancel={() => setToRemove(null)} onConfirm={handleRemove} />
      )}
    </div>
  );
}
