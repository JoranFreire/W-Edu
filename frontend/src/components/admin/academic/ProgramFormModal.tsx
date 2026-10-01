'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { optionsOf, programLevelLabels, programStatusLabels } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { fromOptionalInt, toOptionalInt } from '@/lib/forms/numbers';
import type { ProgramInput } from '@/lib/hooks/admin/academic/usePrograms';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { AcademicUnit, Program, ProgramLevel, ProgramStatus } from '@/types/academic';

export default function ProgramFormModal({ program, units, onSave, onClose }: {
  program?: Program;
  units: AcademicUnit[];
  onSave: (input: ProgramInput) => Promise<void>;
  onClose: () => void;
}) {
  const terms = useTerminology();
  const [form, setForm] = useState({
    code: program?.code ?? '',
    name: program?.name ?? '',
    level: program?.level ?? ('free' as ProgramLevel),
    unit_id: program?.unit_id ?? null,
    degree: program?.degree ?? '',
    duration_terms: fromOptionalInt(program?.duration_terms),
    total_hours: fromOptionalInt(program?.total_hours),
    total_credits: fromOptionalInt(program?.total_credits),
    complementary_hours: fromOptionalInt(program?.complementary_hours),
    internship_hours: fromOptionalInt(program?.internship_hours),
    requires_final_project: program?.requires_final_project ?? false,
    status: program?.status ?? ('draft' as ProgramStatus),
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: ProgramInput = {
      ...form,
      degree: form.degree || null,
      duration_terms: toOptionalInt(form.duration_terms),
      total_hours: toOptionalInt(form.total_hours),
      total_credits: toOptionalInt(form.total_credits),
      complementary_hours: toOptionalInt(form.complementary_hours),
      internship_hours: toOptionalInt(form.internship_hours),
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar programa.')));
  };

  return (
    <Modal title={program ? `Editar: ${program.name}` : terms.newProgram} size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={labelCls}>Código
          <input required value={form.code} onChange={(e) => set({ code: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Nome
          <input required value={form.name} onChange={(e) => set({ name: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Nível
          <select value={form.level} onChange={(e) => set({ level: e.target.value as ProgramLevel })} className={`mt-1 ${inputCls}`}>
            {optionsOf(programLevelLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Unidade
          <select value={form.unit_id ?? ''} onChange={(e) => set({ unit_id: e.target.value ? Number(e.target.value) : null })} className={`mt-1 ${inputCls}`}>
            <option value="">Nenhuma</option>
            {units.map((unit) => <option key={unit.id} value={unit.id}>{unit.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Grau / titulação
          <input value={form.degree} onChange={(e) => set({ degree: e.target.value })} placeholder="Ex.: Bacharelado" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Duração ({terms.term.toLowerCase()}s)
          <input type="number" min={1} value={form.duration_terms} onChange={(e) => set({ duration_terms: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Carga horária total
          <input type="number" min={0} value={form.total_hours} onChange={(e) => set({ total_hours: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Créditos totais
          <input type="number" min={0} value={form.total_credits} onChange={(e) => set({ total_credits: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Atividades complementares (h)
          <input type="number" min={0} value={form.complementary_hours} onChange={(e) => set({ complementary_hours: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Estágio obrigatório (h)
          <input type="number" min={0} value={form.internship_hours} onChange={(e) => set({ internship_hours: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 sm:col-span-2">
          <input type="checkbox" checked={form.requires_final_project} onChange={(e) => set({ requires_final_project: e.target.checked })} />
          Exige trabalho de conclusão (TCC)
        </label>
        <label className={labelCls}>Situação
          <select value={form.status} onChange={(e) => set({ status: e.target.value as ProgramStatus })} className={`mt-1 ${inputCls}`}>
            {optionsOf(programStatusLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
