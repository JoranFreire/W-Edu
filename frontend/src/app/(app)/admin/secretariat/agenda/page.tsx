'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ClassAgendaPanel from '@/components/schoolLife/ClassAgendaPanel';
import ClassGroupPicker from '@/components/schoolLife/ClassGroupPicker';
import BackButton from '@/components/common/BackButton';
import { sectionCls } from '@/components/common/formStyles';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Agenda das turmas para a secretaria (que nao acessa o diario de classe). */
export default function SecretariatAgendaPage() {
  const router = useRouter();
  const { terms, error } = useAcademicTerms();
  const [chosenTerm, setChosenTerm] = useState<number | null>(null);
  const [groupId, setGroupId] = useState<number | null>(null);
  useErrorToast(error, 'Erro ao carregar períodos letivos.');
  const termId = chosenTerm ?? terms.find((term) => term.status === 'open')?.id ?? terms[0]?.id ?? null;

  const changeTerm = (next: number | null) => {
    setChosenTerm(next);
    setGroupId(null);
  };

  return (
    <div className="space-y-6">
      <BackButton label="Secretaria" onClick={() => router.push('/admin/secretariat')} />
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agenda das turmas</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Tarefas, provas, eventos e avisos publicados para alunos e responsáveis.</p>
      </div>
      <section className={sectionCls}>
        <ClassGroupPicker terms={terms} termId={termId} groupId={groupId} onTermChange={changeTerm} onGroupChange={setGroupId} />
      </section>
      {groupId
        ? <ClassAgendaPanel key={groupId} groupId={groupId} offeringId={null} />
        : <p className="text-sm text-gray-500 dark:text-gray-400">Escolha uma turma para ver e publicar na agenda.</p>}
    </div>
  );
}
