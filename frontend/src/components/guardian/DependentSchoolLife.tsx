'use client';

import toast from 'react-hot-toast';
import AgendaList from '@/components/schoolLife/AgendaList';
import OccurrenceList from '@/components/schoolLife/OccurrenceList';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import { useDependentSchoolLife } from '@/lib/hooks/guardian/useDependentSchoolLife';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Occurrence } from '@/types/schoolLife';

/** Ocorrencias (com "Ciente") ou proximos itens da agenda da turma do dependente. */
export default function DependentSchoolLife({ studentId, view }: { studentId: string; view: 'occurrences' | 'agenda' }) {
  const { schoolLife, error, acknowledge } = useDependentSchoolLife(studentId, todayIso());
  useErrorToast(error, 'Erro ao carregar a vida escolar.');

  const handleAcknowledge = async (occurrence: Occurrence) => {
    try {
      await acknowledge(occurrence.id);
      toast.success('Ciência registrada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar a ciência.'));
    }
  };

  if (!schoolLife) return <Spinner variant="panel" />;
  return (
    <section className={sectionCls}>
      {view === 'occurrences'
        ? <OccurrenceList occurrences={schoolLife.occurrences} onAcknowledge={handleAcknowledge} />
        : <AgendaList items={schoolLife.agenda} showGroup />}
    </section>
  );
}
