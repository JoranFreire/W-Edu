'use client';

import toast from 'react-hot-toast';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useStudentOccurrences } from '@/lib/hooks/schoolLife/useStudentOccurrences';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { PersonSummary } from '@/types/academicGroups';
import type { Occurrence } from '@/types/schoolLife';
import OccurrenceForm from './OccurrenceForm';
import OccurrenceList from './OccurrenceList';

/** Ocorrencias do aluno na ficha da secretaria: historico, registro e remocao. */
export default function OccurrencesPanel({ student }: { student: PersonSummary }) {
  const { occurrences, error, register, remove } = useStudentOccurrences(student.id);
  useErrorToast(error, 'Erro ao carregar ocorrências.');

  const handleRemove = async (occurrence: Occurrence) => {
    if (!window.confirm('Remover esta ocorrência?')) return;
    try {
      await remove(occurrence.id);
      toast.success('Ocorrência removida.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível remover.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Ocorrências</h2>
      <OccurrenceForm students={[student]} classGroupId={null} onSubmit={register} />
      <OccurrenceList occurrences={occurrences} onRemove={handleRemove} />
    </section>
  );
}
