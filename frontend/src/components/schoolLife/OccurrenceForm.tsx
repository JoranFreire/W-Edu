'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { occurrenceKindLabels, occurrenceSeverityLabels } from '@/lib/academic/schoolLifeLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import type { PersonSummary } from '@/types/academicGroups';
import type { OccurrenceInput, OccurrenceKind, OccurrenceSeverity } from '@/types/schoolLife';

interface Draft {
  studentId: string | null;
  kind: OccurrenceKind;
  severity: OccurrenceSeverity;
  description: string;
  occurredOn: string;
}

/** Registra ocorrencia; `selectable` mostra a escolha entre `students`, senao vale o primeiro (aluno fixo). */
export default function OccurrenceForm({ students, selectable = false, classGroupId, onSubmit }: {
  students: PersonSummary[];
  selectable?: boolean;
  classGroupId: string | null;
  onSubmit: (input: OccurrenceInput) => Promise<void>;
}) {
  const empty: Draft = {
    studentId: selectable ? null : students[0]?.id ?? null, kind: 'behavior', severity: 'low', description: '', occurredOn: todayIso(),
  };
  const [draft, setDraft] = useState(empty);
  const set = (patch: Partial<Draft>) => setDraft({ ...draft, ...patch });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (draft.studentId === null) return;
    try {
      await onSubmit({
        student_id: draft.studentId, class_group_id: classGroupId, kind: draft.kind, severity: draft.severity,
        description: draft.description, occurred_on: draft.occurredOn,
      });
      setDraft(empty);
      toast.success('Ocorrência registrada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar ocorrência.'));
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        {selectable && (
          <select required aria-label="Aluno da ocorrência" value={draft.studentId ?? ''} onChange={(e) => set({ studentId: e.target.value || null })} className={inputCls}>
            <option value="">Aluno…</option>
            {students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}
          </select>
        )}
        <select aria-label="Tipo de ocorrência" value={draft.kind} onChange={(e) => set({ kind: e.target.value as OccurrenceKind })} className={inputCls}>
          {optionsOf(occurrenceKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <select aria-label="Gravidade" value={draft.severity} onChange={(e) => set({ severity: e.target.value as OccurrenceSeverity })} className={inputCls}>
          {optionsOf(occurrenceSeverityLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <input required type="date" aria-label="Data da ocorrência" value={draft.occurredOn} onChange={(e) => set({ occurredOn: e.target.value })} className={inputCls} />
      </div>
      <textarea required aria-label="Descrição da ocorrência" value={draft.description} onChange={(e) => set({ description: e.target.value })}
        placeholder="O que aconteceu" rows={2} className={inputCls} />
      <div className="flex justify-end">
        <button className={primaryButtonCls}>Registrar ocorrência</button>
      </div>
    </form>
  );
}
