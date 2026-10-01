'use client';

import { inputCls } from '@/components/common/formStyles';
import { useClassGroups } from '@/lib/hooks/admin/academic/useClassGroups';
import type { AcademicTerm } from '@/types/academicCalendar';

/** Escolha do periodo letivo e da turma-grupo (sem periodo escolhido, vale `termId` padrao do pai). */
export default function ClassGroupPicker({ terms, termId, groupId, onTermChange, onGroupChange }: {
  terms: AcademicTerm[];
  termId: number | null;
  groupId: number | null;
  onTermChange: (termId: number | null) => void;
  onGroupChange: (groupId: number | null) => void;
}) {
  const { groups } = useClassGroups(termId ?? undefined);
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
      <select aria-label="Período letivo" value={termId ?? ''} onChange={(e) => onTermChange(Number(e.target.value) || null)} className={inputCls}>
        <option value="">Período letivo…</option>
        {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
      </select>
      <select aria-label="Turma" value={groupId ?? ''} onChange={(e) => onGroupChange(Number(e.target.value) || null)} className={inputCls} disabled={!termId}>
        <option value="">Turma…</option>
        {groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}
      </select>
    </div>
  );
}
