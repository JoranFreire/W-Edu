'use client';

import { useState } from 'react';
import { TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { type SubjectLinkKind, useSubjectLinks } from '@/lib/hooks/admin/academic/useSubjectLinks';
import type { Subject } from '@/types/academic';

const texts: Record<SubjectLinkKind, { title: string; empty: string; add: string }> = {
  prerequisites: { title: 'Pré-requisitos', empty: 'Sem pré-requisitos.', add: 'Adicionar pré-requisito' },
  equivalences: { title: 'Equivalências', empty: 'Sem equivalências.', add: 'Adicionar equivalência' },
};

/** Lista e edita um tipo de vinculo (pre-requisito ou equivalencia) de uma disciplina. */
export default function SubjectLinkList({ kind, subject, subjects, canRemove }: {
  kind: SubjectLinkKind;
  subject: Subject;
  subjects: Subject[];
  canRemove: boolean;
}) {
  const { links, add, remove } = useSubjectLinks(kind, subject.id);
  const [selected, setSelected] = useState('');
  const linkedIds = new Set(links.map((link) => link.id));
  const candidates = subjects.filter((candidate) => candidate.id !== subject.id && !linkedIds.has(candidate.id));
  const text = texts[kind];

  const handleAdd = async () => {
    if (!selected) return;
    try {
      await add(Number(selected));
      setSelected('');
    } catch (error) {
      toast.error(apiErrorMessage(error, `Erro: ${text.add.toLowerCase()}.`));
    }
  };

  const handleRemove = async (otherId: number) => {
    try { await remove(otherId); } catch (error) { toast.error(apiErrorMessage(error, 'Erro ao remover vínculo.')); }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{text.title}</h3>
      {links.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">{text.empty}</p>
      ) : (
        <ul className="space-y-1">
          {links.map((link) => (
            <li key={link.id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm dark:bg-gray-900">
              <span className="text-gray-800 dark:text-gray-200">{link.code} · {link.name}</span>
              {canRemove && (
                <button onClick={() => handleRemove(link.id)} aria-label={`Remover ${link.code}`} className={dangerIconButtonCls}>
                  <TrashIcon className="h-4 w-4" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      <div className="flex gap-2">
        <select aria-label={text.add} value={selected} onChange={(e) => setSelected(e.target.value)} className={inputCls}>
          <option value="">Selecione...</option>
          {candidates.map((candidate) => <option key={candidate.id} value={candidate.id}>{candidate.code} · {candidate.name}</option>)}
        </select>
        <button type="button" onClick={handleAdd} disabled={!selected} className={secondaryButtonCls}>Adicionar</button>
      </div>
    </div>
  );
}
