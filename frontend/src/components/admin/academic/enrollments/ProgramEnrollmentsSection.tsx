'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import SectionHeader from '@/components/common/SectionHeader';
import { inputCls, sectionCls } from '@/components/common/formStyles';
import { enrollmentStatusLabels, optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { type ProgramEnrollmentInput, useProgramEnrollments } from '@/lib/hooks/admin/academic/useProgramEnrollments';
import { usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import { useInstitutionUsers } from '@/lib/hooks/admin/useInstitutionUsers';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { ProgramEnrollment, ProgramEnrollmentStatus } from '@/types/academicGroups';
import EnrollmentStatusSelect from './EnrollmentStatusSelect';
import ProgramEnrollmentFormModal from './ProgramEnrollmentFormModal';

export default function ProgramEnrollmentsSection() {
  const labels = useTerminology();
  const [programId, setProgramId] = useState<number | undefined>();
  const [status, setStatus] = useState<ProgramEnrollmentStatus | undefined>();
  const { enrollments, error, create, changeStatus } = useProgramEnrollments({ program_id: programId, status });
  const { programs } = usePrograms();
  const { terms } = useAcademicTerms();
  const { users } = useInstitutionUsers();
  const [creating, setCreating] = useState(false);
  useErrorToast(error, 'Erro ao carregar matrículas.');

  const handleCreate = async (input: ProgramEnrollmentInput) => {
    const created = await create(input);
    toast.success(`Matrícula ${created.registration_number} criada.`);
    setCreating(false);
  };

  const handleStatus = async (enrollment: ProgramEnrollment, next: ProgramEnrollmentStatus) => {
    if (!window.confirm(`Alterar a matrícula ${enrollment.registration_number} para "${enrollmentStatusLabels[next]}"?`)) return;
    try {
      await changeStatus(enrollment.id, next);
      toast.success('Situação atualizada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao alterar situação.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader title="Matrículas" description={`Vínculo do aluno com o ${labels.program.toLowerCase()} e número de matrícula.`} actionLabel="Nova matrícula" onAction={() => setCreating(true)} />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <select aria-label="Filtrar por programa" value={programId ?? ''} onChange={(e) => setProgramId(e.target.value ? Number(e.target.value) : undefined)} className={inputCls}>
          <option value="">Todos os programas</option>
          {programs.map((program) => <option key={program.id} value={program.id}>{program.code} · {program.name}</option>)}
        </select>
        <select aria-label="Filtrar por situação" value={status ?? ''} onChange={(e) => setStatus((e.target.value || undefined) as ProgramEnrollmentStatus | undefined)} className={inputCls}>
          <option value="">Todas as situações</option>
          {optionsOf(enrollmentStatusLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
      {enrollments.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma matrícula encontrada.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-xs uppercase text-gray-500 dark:text-gray-400">
              <tr><th className="py-2 pr-4">Matrícula</th><th className="py-2 pr-4">Aluno</th><th className="py-2 pr-4">Programa</th><th className="py-2 pr-4">Desde</th><th className="py-2">Situação</th></tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {enrollments.map((enrollment) => (
                <tr key={enrollment.id} className="text-gray-800 dark:text-gray-200">
                  <td className="py-2 pr-4 font-mono">{enrollment.registration_number}</td>
                  <td className="py-2 pr-4">{enrollment.student.name}</td>
                  <td className="py-2 pr-4">{enrollment.program.code}</td>
                  <td className="py-2 pr-4">{formatIsoDate(enrollment.enrolled_on)}</td>
                  <td className="py-2"><EnrollmentStatusSelect enrollment={enrollment} onChange={(next) => handleStatus(enrollment, next)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {creating && (
        <ProgramEnrollmentFormModal students={users.filter((user) => user.role === 'student')} programs={programs} terms={terms}
          onSave={handleCreate} onClose={() => setCreating(false)} />
      )}
    </section>
  );
}
