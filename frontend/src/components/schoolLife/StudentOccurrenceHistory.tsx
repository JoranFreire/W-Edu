'use client';

import toast from 'react-hot-toast';
import { apiErrorMessage } from '@/lib/api/errors';
import { useStudentOccurrences } from '@/lib/hooks/schoolLife/useStudentOccurrences';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { canRemoveSchoolRecord } from '@/lib/schoolLife/removalRules';
import { useAuthStore } from '@/store/authStore';
import type { Occurrence } from '@/types/schoolLife';
import OccurrenceList from './OccurrenceList';
import { useCurrentRoles } from '@/lib/hooks/useCurrentRoles';

/** Historico de ocorrencias de um aluno para o professor; remove so as que ele registrou. */
export default function StudentOccurrenceHistory({ studentId }: { studentId: string }) {
  const user = useAuthStore((state) => state.student);
  const { roles } = useCurrentRoles();
  const { occurrences, error, remove } = useStudentOccurrences(studentId);
  useErrorToast(error, 'Erro ao carregar o histórico do aluno.');

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
    <OccurrenceList
      occurrences={occurrences}
      onRemove={handleRemove}
      canRemove={(occurrence) => canRemoveSchoolRecord(user?.id, roles, occurrence.reported_by?.id)}
    />
  );
}
