'use client';

import { useState } from 'react';
import { ClipboardDocumentCheckIcon, LockClosedIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, iconButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { type DiaryEntryInput, useClassDiary } from '@/lib/hooks/teaching/useClassDiary';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { DiaryEntry } from '@/types/assessment';
import DiaryAttendanceModal from './DiaryAttendanceModal';
import DiaryEntryForm from './DiaryEntryForm';

/** Diario de classe: aulas registradas e chamada de cada uma. */
export default function DiaryPanel({ offeringId, onAttendanceChanged }: { offeringId: number; onAttendanceChanged: () => void }) {
  const { entries, error, create, remove } = useClassDiary(offeringId);
  const [calling, setCalling] = useState<DiaryEntry | null>(null);
  useErrorToast(error, 'Erro ao carregar diário.');

  const handleCreate = async (input: DiaryEntryInput) => {
    await create(input);
    onAttendanceChanged();
  };

  const handleRemove = async (entry: DiaryEntry) => {
    if (!window.confirm(`Excluir a aula de ${formatIsoDate(entry.date)} e sua chamada?`)) return;
    try {
      await remove(entry.id);
      onAttendanceChanged();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir aula.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Diário de classe</h2>
      <DiaryEntryForm onCreate={handleCreate} />
      {entries.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma aula registrada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {entries.map((entry) => (
            <li key={entry.id} className="flex items-start justify-between gap-3 py-3">
              <div className="min-w-0">
                <p className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white">
                  {formatIsoDate(entry.date)} · {entry.lesson_count} aula{entry.lesson_count > 1 ? 's' : ''}
                  {entry.locked && <LockClosedIcon className="h-4 w-4 text-gray-400" aria-label="Etapa encerrada" />}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">{entry.content_taught}</p>
              </div>
              <div className="flex shrink-0 items-center gap-1">
                <button onClick={() => setCalling(entry)} aria-label={`Chamada de ${formatIsoDate(entry.date)}`} className={iconButtonCls}>
                  <ClipboardDocumentCheckIcon className="h-4 w-4" />
                </button>
                {!entry.locked && (
                  <button onClick={() => handleRemove(entry)} aria-label={`Excluir aula de ${formatIsoDate(entry.date)}`} className={dangerIconButtonCls}>
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {calling && <DiaryAttendanceModal entry={calling} onSaved={onAttendanceChanged} onClose={() => setCalling(null)} />}
    </section>
  );
}
