'use client';

import toast from 'react-hot-toast';
import Modal from '@/components/common/Modal';
import Spinner from '@/components/common/Spinner';
import { secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useGrades } from '@/lib/hooks/teaching/useGrades';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { AssessmentItem } from '@/types/assessment';
import GradeEntryForm from './GradeEntryForm';

export default function GradeEntryModal({ item, onClose, onSaved }: { item: AssessmentItem; onClose: () => void; onSaved: () => void }) {
  const { rows, error, save, importQuiz } = useGrades(item.id);
  useErrorToast(error, 'Erro ao carregar notas.');

  const handleImport = async () => {
    try {
      const result = await importQuiz();
      toast.success(`${result.imported} nota(s) importada(s); ${result.without_attempt} sem tentativa.`);
      onSaved();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao importar notas do quiz.'));
    }
  };

  const handleSave = async (grades: Parameters<typeof save>[0]) => {
    await save(grades);
    onSaved();
  };

  return (
    <Modal title={`Notas: ${item.name}`} description={`Nota máxima ${item.max_score}`} size="md" onClose={onClose}>
      {item.kind === 'quiz' && item.quiz_id && (
        <button type="button" onClick={handleImport} className={`${secondaryButtonCls} mb-4 w-full`}>Importar melhor tentativa do quiz</button>
      )}
      {rows ? (
        <GradeEntryForm key={rows.map((row) => `${row.class_enrollment_id}:${row.score}`).join('|')} rows={rows} maxScore={item.max_score} onSave={handleSave} onClose={onClose} />
      ) : (
        <Spinner variant="panel" />
      )}
    </Modal>
  );
}
