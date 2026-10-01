'use client';

import { sectionCls } from '@/components/common/formStyles';
import { useOccurrenceRegistration } from '@/lib/hooks/schoolLife/useOccurrenceRegistration';
import type { PersonSummary } from '@/types/academicGroups';
import OccurrenceForm from './OccurrenceForm';

/** Professor registra ocorrencia de um aluno da turma; o historico fica na ficha da secretaria. */
export default function ClassOccurrencePanel({ students, classGroupId }: { students: PersonSummary[]; classGroupId: number | null }) {
  const { register } = useOccurrenceRegistration();
  return (
    <section className={`${sectionCls} space-y-4`}>
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Registrar ocorrência</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Os responsáveis do aluno são avisados e podem dar ciência no portal.</p>
      </div>
      {students.length === 0
        ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno inscrito nesta turma.</p>
        : <OccurrenceForm students={students} selectable classGroupId={classGroupId} onSubmit={register} />}
    </section>
  );
}
