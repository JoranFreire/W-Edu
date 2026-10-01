'use client';

import { inputCls } from '@/components/common/formStyles';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useClassGroups } from '@/lib/hooks/admin/academic/useClassGroups';
import { useSubjects } from '@/lib/hooks/admin/academic/useSubjects';
import { useTerminology } from '@/lib/hooks/useTerminology';

export interface OfferingAcademicValue {
  term_id: string;
  subject_id: string;
  class_group_id: string;
}

/** Vinculos academicos opcionais da oferta: periodo letivo, disciplina e turma-grupo. */
export default function OfferingAcademicFields({ value, onChange }: {
  value: OfferingAcademicValue;
  onChange: (value: OfferingAcademicValue) => void;
}) {
  const labels = useTerminology();
  const { terms } = useAcademicTerms();
  const { subjects } = useSubjects();
  const { groups } = useClassGroups(value.term_id ? value.term_id : undefined);

  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
      <select aria-label={labels.academicTerm} value={value.term_id} onChange={(e) => onChange({ ...value, term_id: e.target.value, class_group_id: '' })} className={inputCls}>
        <option value="">{labels.academicTerm} (opcional)</option>
        {terms.filter((term) => term.status !== 'closed').map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
      </select>
      <select aria-label={labels.subject} value={value.subject_id} onChange={(e) => onChange({ ...value, subject_id: e.target.value })} className={inputCls}>
        <option value="">{labels.subject} (opcional)</option>
        {subjects.filter((subject) => subject.is_active).map((subject) => <option key={subject.id} value={subject.id}>{subject.code} · {subject.name}</option>)}
      </select>
      <select aria-label="Turma-grupo" value={value.class_group_id} disabled={!value.term_id} onChange={(e) => onChange({ ...value, class_group_id: e.target.value })} className={inputCls}>
        <option value="">Turma-grupo (opcional)</option>
        {groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}
      </select>
    </div>
  );
}
