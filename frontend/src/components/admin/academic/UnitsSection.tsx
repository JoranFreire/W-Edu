'use client';

import { useState } from 'react';
import { BuildingOffice2Icon, PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import SectionHeader from '@/components/common/SectionHeader';
import { dangerIconButtonCls, iconButtonCls, sectionCls } from '@/components/common/formStyles';
import { unitKindLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { type AcademicUnitInput, useAcademicUnits } from '@/lib/hooks/admin/academic/useAcademicUnits';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { AcademicUnit } from '@/types/academic';
import UnitFormModal from './UnitFormModal';
import { flattenUnits } from '@/lib/academic/unitTree';

export default function UnitsSection({ canDelete }: { canDelete: boolean }) {
  const { units, error, save, remove } = useAcademicUnits();
  const [editing, setEditing] = useState<{ unit?: AcademicUnit } | null>(null);
  const [toDelete, setToDelete] = useState<AcademicUnit | null>(null);
  useErrorToast(error, 'Erro ao carregar unidades.');

  const handleSave = async (input: AcademicUnitInput) => {
    await save(editing?.unit?.id ?? null, input);
    toast.success(editing?.unit ? 'Unidade atualizada.' : 'Unidade criada.');
    setEditing(null);
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await remove(toDelete);
      toast.success('Unidade excluída.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir unidade.'));
    }
    setToDelete(null);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader
        title="Unidades acadêmicas"
        description="Segmentos, faculdades, departamentos ou eixos que agrupam os programas."
        actionLabel="Nova unidade"
        onAction={() => setEditing({})}
      />
      {units.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma unidade cadastrada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {flattenUnits(units).map(({ unit, depth }) => (
            <li key={unit.id} className="flex items-center justify-between gap-3 py-3" style={{ paddingLeft: `${depth * 1.5}rem` }}>
              <div className="flex min-w-0 items-center gap-3">
                <BuildingOffice2Icon className="h-5 w-5 shrink-0 text-indigo-500" />
                <div className="min-w-0">
                  <p className="truncate font-medium text-gray-900 dark:text-white">{unit.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{unitKindLabels[unit.kind]}</p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => setEditing({ unit })} aria-label={`Editar unidade ${unit.name}`} className={iconButtonCls}>
                  <PencilSquareIcon className="h-4 w-4" />
                </button>
                {canDelete && (
                  <button onClick={() => setToDelete(unit)} aria-label={`Excluir unidade ${unit.name}`} className={dangerIconButtonCls}>
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editing && <UnitFormModal unit={editing.unit} units={units} onSave={handleSave} onClose={() => setEditing(null)} />}
      {toDelete && (
        <ConfirmDialog title="Excluir unidade" message={`Excluir "${toDelete.name}"?`} confirmLabel="Excluir" danger
          onCancel={() => setToDelete(null)} onConfirm={handleDelete} />
      )}
    </section>
  );
}
