'use client';

import Modal from '@/components/common/Modal';
import Spinner from '@/components/common/Spinner';
import { formatIsoDate } from '@/lib/dates';
import { type DiaryAttendanceInput, useDiaryAttendance } from '@/lib/hooks/teaching/useDiaryAttendance';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { DiaryEntry } from '@/types/assessment';
import DiaryAttendanceForm from './DiaryAttendanceForm';

export default function DiaryAttendanceModal({ entry, onClose, onSaved }: { entry: DiaryEntry; onClose: () => void; onSaved: () => void }) {
  const { rows, error, save } = useDiaryAttendance(entry.id);
  useErrorToast(error, 'Erro ao carregar chamada.');

  const handleSave = async (values: DiaryAttendanceInput[]) => {
    await save(values);
    onSaved();
  };

  return (
    <Modal
      title={`Chamada de ${formatIsoDate(entry.date)}`}
      description={`${entry.lesson_count} aula(s)${entry.locked ? ' · etapa encerrada (somente leitura)' : ''}`}
      size="lg"
      onClose={onClose}
    >
      {rows ? (
        <DiaryAttendanceForm rows={rows} lessonCount={entry.lesson_count} readOnly={entry.locked} onSave={handleSave} onClose={onClose} />
      ) : (
        <Spinner variant="panel" />
      )}
    </Modal>
  );
}
