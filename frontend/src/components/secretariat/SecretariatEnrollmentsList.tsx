'use client';

import { useState } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import ProgramEnrollmentFormModal from '@/components/admin/academic/enrollments/ProgramEnrollmentFormModal';
import SectionHeader from '@/components/common/SectionHeader';
import { inputCls, sectionCls } from '@/components/common/formStyles';
import { enrollmentStatusLabels } from '@/lib/academic/labels';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { type ProgramEnrollmentInput, useProgramEnrollments } from '@/lib/hooks/admin/academic/useProgramEnrollments';
import { usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import { useSecretariatStudents } from '@/lib/hooks/secretariat/useSecretariatStudents';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Busca de matriculas por aluno ou numero, com acesso a ficha e nova matricula. */
export default function SecretariatEnrollmentsList() {
  const [programId, setProgramId] = useState<string | undefined>();
  const [search, setSearch] = useState('');
  const [creating, setCreating] = useState(false);
  const { enrollments, error, create } = useProgramEnrollments({ program_id: programId });
  const { programs } = usePrograms();
  const { terms } = useAcademicTerms();
  const { students } = useSecretariatStudents();
  useErrorToast(error, 'Erro ao carregar matrículas.');

  const term = search.trim().toLowerCase();
  const visible = term
    ? enrollments.filter((e) => `${e.student.name} ${e.student.email} ${e.registration_number}`.toLowerCase().includes(term))
    : enrollments;

  const handleCreate = async (input: ProgramEnrollmentInput) => {
    const created = await create(input);
    toast.success(`Matrícula ${created.registration_number} criada.`);
    setCreating(false);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader title="Matrículas" description="Localize o aluno para ver o histórico, movimentar a matrícula ou registrar aproveitamento." actionLabel="Nova matrícula" onAction={() => setCreating(true)} />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <input aria-label="Buscar matrícula" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Nome, e-mail ou número de matrícula" className={inputCls} />
        <select aria-label="Filtrar por programa" value={programId ?? ''} onChange={(e) => setProgramId(e.target.value || undefined)} className={inputCls}>
          <option value="">Todos os programas</option>
          {programs.map((program) => <option key={program.id} value={program.id}>{program.code} · {program.name}</option>)}
        </select>
      </div>
      {visible.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma matrícula encontrada.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {visible.map((enrollment) => (
            <li key={enrollment.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <Link href={`/admin/secretariat/enrollments/${enrollment.id}`} className="min-w-0">
                <p className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">{enrollment.student.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400"><span className="font-mono">{enrollment.registration_number}</span> · {enrollment.program.code}</p>
              </Link>
              <span className="text-sm text-gray-600 dark:text-gray-300">{enrollmentStatusLabels[enrollment.status]}</span>
            </li>
          ))}
        </ul>
      )}
      {creating && <ProgramEnrollmentFormModal students={students} programs={programs} terms={terms} onSave={handleCreate} onClose={() => setCreating(false)} />}
    </section>
  );
}
