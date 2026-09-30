'use client';

import { useState } from 'react';
import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import SectionHeader from '@/components/common/SectionHeader';
import { dangerIconButtonCls, iconButtonCls, sectionCls } from '@/components/common/formStyles';
import { averageFormulaLabels, formatScore, gradingScaleLabels } from '@/lib/academic/assessmentLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { type GradingSchemeInput, useGradingSchemes } from '@/lib/hooks/admin/academic/useGradingSchemes';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { GradingScheme } from '@/types/assessment';
import GradingSchemeFormModal from './GradingSchemeFormModal';

export default function GradingSchemesSection({ canDelete }: { canDelete: boolean }) {
  const { schemes, error, save, remove } = useGradingSchemes();
  const [editing, setEditing] = useState<{ scheme?: GradingScheme } | null>(null);
  const [toDelete, setToDelete] = useState<GradingScheme | null>(null);
  useErrorToast(error, 'Erro ao carregar esquemas.');

  const handleSave = async (input: GradingSchemeInput) => {
    await save(editing?.scheme?.id ?? null, input);
    toast.success('Esquema salvo.');
    setEditing(null);
  };

  const handleDelete = async () => {
    if (!toDelete?.id) return;
    try {
      await remove(toDelete.id);
      toast.success('Esquema excluído.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir esquema.'));
    }
    setToDelete(null);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader
        title="Esquemas de avaliação"
        description="Escala, média de aprovação, cálculo e frequência mínima. Sem esquema, vale 0 a 10, média 6 e 75%."
        actionLabel="Novo esquema"
        onAction={() => setEditing({})}
      />
      {schemes.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum esquema cadastrado.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {schemes.map((scheme) => (
            <li key={scheme.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  {scheme.name}
                  {scheme.is_default && <span className="ml-2 rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">padrão</span>}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {gradingScaleLabels[scheme.scale]} · {formatScore(scheme.min_value)} a {formatScore(scheme.max_value)} · aprovação {formatScore(scheme.passing_grade)}
                  {' · '}{averageFormulaLabels[scheme.formula]} · frequência {scheme.min_attendance}%
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => setEditing({ scheme })} aria-label={`Editar esquema ${scheme.name}`} className={iconButtonCls}><PencilSquareIcon className="h-4 w-4" /></button>
                {canDelete && (
                  <button onClick={() => setToDelete(scheme)} aria-label={`Excluir esquema ${scheme.name}`} className={dangerIconButtonCls}><TrashIcon className="h-4 w-4" /></button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editing && <GradingSchemeFormModal scheme={editing.scheme} onSave={handleSave} onClose={() => setEditing(null)} />}
      {toDelete && (
        <ConfirmDialog title="Excluir esquema" message={`Excluir "${toDelete.name}"?`} confirmLabel="Excluir" danger
          onCancel={() => setToDelete(null)} onConfirm={handleDelete} />
      )}
    </section>
  );
}
