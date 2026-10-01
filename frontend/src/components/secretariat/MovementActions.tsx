'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { secondaryButtonCls } from '@/components/common/formStyles';
import { curriculumStatusLabels } from '@/lib/academic/labels';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useCurricula } from '@/lib/hooks/admin/academic/useCurricula';
import { usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import type { useEnrollmentFile } from '@/lib/hooks/secretariat/useEnrollmentFile';
import { type Movement, movementLabels, movementsByStatus } from '@/lib/secretariat/movements';
import type { ProgramEnrollment } from '@/types/academicGroups';
import MovementModal, { type MovementField } from './MovementModal';

type FileActions = Pick<ReturnType<typeof useEnrollmentFile>, 'move' | 'reenroll' | 'transferOut' | 'transferInternal' | 'changeCurriculum'>;

/** Botoes das movimentacoes permitidas e o formulario de cada uma. */
export default function MovementActions({ enrollment, actions, onChanged }: { enrollment: ProgramEnrollment; actions: FileActions; onChanged: () => void }) {
  const router = useRouter();
  const { terms } = useAcademicTerms();
  const { programs } = usePrograms();
  const { curricula } = useCurricula(enrollment.program.id);
  const [open, setOpen] = useState<Movement | null>(null);

  const fields: Record<Movement, MovementField[]> = {
    reenroll: [
      { name: 'term_id', label: 'Período letivo', required: true, options: terms.filter((t) => t.status !== 'closed').map((t) => ({ value: String(t.id), label: t.name })) },
      { name: 'term_number', label: 'Série/semestre (opcional)' },
    ],
    lock: [], reactivate: [], cancel: [], drop: [],
    'transfer-out': [{ name: 'destination', label: 'Instituição de destino', required: true }],
    'transfer-internal': [{
      name: 'program_id', label: 'Novo programa', required: true,
      options: programs.filter((p) => p.id !== enrollment.program.id).map((p) => ({ value: String(p.id), label: `${p.code} · ${p.name}` })),
    }],
    'change-curriculum': [{
      name: 'curriculum_id', label: 'Nova matriz', required: true,
      options: curricula.filter((c) => c.status !== 'draft' && c.id !== enrollment.curriculum_id)
        .map((c) => ({ value: String(c.id), label: `Versão ${c.version} (${curriculumStatusLabels[c.status]})` })),
    }],
  };

  const submit = async (movement: Movement, values: Record<string, string>) => {
    const reason = values.reason?.trim() || null;
    if (movement === 'reenroll') await actions.reenroll(values.term_id, values.term_number ? Number(values.term_number) : null);
    else if (movement === 'transfer-out') await actions.transferOut(values.destination, reason);
    else if (movement === 'change-curriculum') await actions.changeCurriculum(values.curriculum_id, reason);
    else if (movement === 'transfer-internal') {
      const created = await actions.transferInternal(values.program_id, reason);
      toast.success(`Nova matrícula ${created.registration_number}.`);
      router.push(`/admin/secretariat/enrollments/${created.id}`);
      return;
    } else await actions.move(movement, reason);
    toast.success(`${movementLabels[movement]}: registrado.`);
    setOpen(null);
    onChanged();
  };

  const available = movementsByStatus[enrollment.status];
  if (available.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {available.map((movement) => (
        <button key={movement} onClick={() => setOpen(movement)} className={secondaryButtonCls}>{movementLabels[movement]}</button>
      ))}
      {open && (
        <MovementModal title={movementLabels[open]} fields={fields[open]} onSubmit={(values) => submit(open, values)} onClose={() => setOpen(null)} />
      )}
    </div>
  );
}
