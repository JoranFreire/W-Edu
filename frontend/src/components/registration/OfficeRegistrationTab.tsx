'use client';

import { useState } from 'react';
import { inputCls, sectionCls } from '@/components/common/formStyles';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useTerminology } from '@/lib/hooks/useTerminology';
import OfficeRegistrationPanel from './OfficeRegistrationPanel';

/** Aba "Disciplinas" da ficha: escolha do periodo e inscricoes do aluno nele. */
export default function OfficeRegistrationTab({ enrollmentId, editable }: { enrollmentId: number; editable: boolean }) {
  const labels = useTerminology();
  const { terms } = useAcademicTerms();
  const [chosen, setChosen] = useState<number | null>(null);
  const termId = chosen ?? terms.find((term) => term.status === 'open')?.id ?? terms[0]?.id ?? null;

  return (
    <section className={`${sectionCls} space-y-4`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">{labels.subjects} no período</h2>
        <select aria-label="Período das disciplinas" value={termId ?? ''} onChange={(e) => setChosen(Number(e.target.value) || null)} className={`${inputCls} md:w-64`}>
          {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
        </select>
      </div>
      {termId
        ? <OfficeRegistrationPanel key={termId} enrollmentId={enrollmentId} termId={termId} editable={editable} />
        : <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum período letivo cadastrado.</p>}
    </section>
  );
}
