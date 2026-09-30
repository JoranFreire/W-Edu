'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { averageFormulaLabels, gradingScaleLabels } from '@/lib/academic/assessmentLabels';
import { formatConceptBands, parseConceptBands } from '@/lib/academic/conceptBands';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import type { GradingSchemeInput } from '@/lib/hooks/admin/academic/useGradingSchemes';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { AverageFormula, GradingScale, GradingScheme } from '@/types/assessment';

export default function GradingSchemeFormModal({ scheme, onSave, onClose }: {
  scheme?: GradingScheme;
  onSave: (input: GradingSchemeInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState({
    name: scheme?.name ?? '',
    scale: scheme?.scale ?? ('numeric' as GradingScale),
    min_value: String(scheme?.min_value ?? 0),
    max_value: String(scheme?.max_value ?? 10),
    passing_grade: String(scheme?.passing_grade ?? 6),
    formula: scheme?.formula ?? ('weighted' as AverageFormula),
    recovery_enabled: scheme?.recovery_enabled ?? true,
    min_attendance: String(scheme?.min_attendance ?? 75),
    concepts: formatConceptBands(scheme?.concepts ?? []),
    is_default: scheme?.is_default ?? false,
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: GradingSchemeInput = {
      ...form,
      min_value: Number(form.min_value),
      max_value: Number(form.max_value),
      passing_grade: Number(form.passing_grade),
      min_attendance: Number(form.min_attendance),
      concepts: form.scale === 'concept' ? parseConceptBands(form.concepts) : [],
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar esquema.')));
  };

  return (
    <Modal title={scheme ? `Editar: ${scheme.name}` : 'Novo esquema de avaliação'} size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={`${labelCls} sm:col-span-2`}>Nome
          <input required value={form.name} onChange={(e) => set({ name: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Escala
          <select value={form.scale} onChange={(e) => set({ scale: e.target.value as GradingScale })} className={`mt-1 ${inputCls}`}>
            {optionsOf(gradingScaleLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Cálculo da média
          <select value={form.formula} onChange={(e) => set({ formula: e.target.value as AverageFormula })} className={`mt-1 ${inputCls}`}>
            {optionsOf(averageFormulaLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Nota mínima
          <input type="number" step="0.1" value={form.min_value} onChange={(e) => set({ min_value: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Nota máxima
          <input type="number" step="0.1" value={form.max_value} onChange={(e) => set({ max_value: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Média para aprovação
          <input type="number" step="0.1" value={form.passing_grade} onChange={(e) => set({ passing_grade: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Frequência mínima (%)
          <input type="number" min={0} max={100} value={form.min_attendance} onChange={(e) => set({ min_attendance: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        {form.scale === 'concept' && (
          <label className={`${labelCls} sm:col-span-2`}>Faixas de conceito (código:nota mínima)
            <input value={form.concepts} onChange={(e) => set({ concepts: e.target.value })} placeholder="A:9, B:7, C:5, D:0" className={`mt-1 ${inputCls}`} />
          </label>
        )}
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input type="checkbox" checked={form.recovery_enabled} onChange={(e) => set({ recovery_enabled: e.target.checked })} className="h-4 w-4 rounded border-gray-300" />
          Permite recuperação
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input type="checkbox" checked={form.is_default} onChange={(e) => set({ is_default: e.target.checked })} className="h-4 w-4 rounded border-gray-300" />
          Padrão da instituição
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
