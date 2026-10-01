'use client';

import { useState } from 'react';
import { inputCls, sectionCls } from '@/components/common/formStyles';
import { useOccurrenceRegistration } from '@/lib/hooks/schoolLife/useOccurrenceRegistration';
import type { PersonSummary } from '@/types/academicGroups';
import type { OccurrenceInput } from '@/types/schoolLife';
import OccurrenceForm from './OccurrenceForm';
import StudentOccurrenceHistory from './StudentOccurrenceHistory';

/** Professor registra ocorrencia de um aluno da turma e consulta o historico dele. */
export default function ClassOccurrencePanel({ students, classGroupId }: { students: PersonSummary[]; classGroupId: string | null }) {
  const { register } = useOccurrenceRegistration();
  const [historyOf, setHistoryOf] = useState<string | null>(null);
  // Muda a cada registro para recarregar o historico exibido.
  const [version, setVersion] = useState(0);

  const handleRegister = async (input: OccurrenceInput) => {
    await register(input);
    setHistoryOf(input.student_id);
    setVersion((current) => current + 1);
  };

  if (students.length === 0) {
    return <section className={sectionCls}><p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aluno inscrito nesta turma.</p></section>;
  }
  return (
    <div className="space-y-6">
      <section className={`${sectionCls} space-y-4`}>
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Registrar ocorrência</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Os responsáveis do aluno são avisados e podem dar ciência no portal.</p>
        </div>
        <OccurrenceForm students={students} selectable classGroupId={classGroupId} onSubmit={handleRegister} />
      </section>
      <section className={`${sectionCls} space-y-4`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Histórico do aluno</h2>
          <select aria-label="Aluno do histórico" value={historyOf ?? ''} onChange={(e) => setHistoryOf(e.target.value || null)} className={`${inputCls} md:w-72`}>
            <option value="">Aluno…</option>
            {students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}
          </select>
        </div>
        {historyOf
          ? <StudentOccurrenceHistory key={`${historyOf}-${version}`} studentId={historyOf} />
          : <p className="text-sm text-gray-500 dark:text-gray-400">Escolha um aluno para ver as ocorrências registradas por toda a equipe.</p>}
      </section>
    </div>
  );
}
