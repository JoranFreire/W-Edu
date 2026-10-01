'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { PersonSummary } from '@/types/academicGroups';
import type { FinalProject, FinalProjectInput } from '@/types/completion';

/** Tema e orientacao do TCC (secretaria); salvar depois de reprovado abre nova tentativa. */
export default function FinalProjectForm({ project, advisors, onSave }: {
  project: FinalProject | null;
  advisors: PersonSummary[];
  onSave: (input: FinalProjectInput) => Promise<void>;
}) {
  const [draft, setDraft] = useState({
    title: project?.title ?? '', advisorId: String(project?.advisor?.id ?? ''), coAdvisor: project?.co_advisor_name ?? '',
  });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSave({ title: draft.title, advisor_id: draft.advisorId ? Number(draft.advisorId) : null, co_advisor_name: draft.coAdvisor || null, notes: null });
      toast.success('TCC salvo.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar o TCC.'));
    }
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-4">
      <input required aria-label="Título do TCC" value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} placeholder="Tema / título" className={`${inputCls} md:col-span-2`} />
      <select aria-label="Orientador do TCC" value={draft.advisorId} onChange={(e) => setDraft({ ...draft, advisorId: e.target.value })} className={inputCls}>
        <option value="">Sem orientador</option>
        {advisors.map((advisor) => <option key={advisor.id} value={advisor.id}>{advisor.name}</option>)}
      </select>
      <input aria-label="Coorientador" value={draft.coAdvisor} onChange={(e) => setDraft({ ...draft, coAdvisor: e.target.value })} placeholder="Coorientação (opcional)" className={inputCls} />
      <div className="flex justify-end md:col-span-4">
        <button className={primaryButtonCls}>{project?.status === 'failed' ? 'Abrir nova tentativa' : 'Salvar TCC'}</button>
      </div>
    </form>
  );
}
