'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { DiaryEntryInput } from '@/lib/hooks/teaching/useClassDiary';

const today = () => new Date().toISOString().slice(0, 10);

/** Registro de uma aula: data, quantidade de aulas e conteudo ministrado. */
export default function DiaryEntryForm({ onCreate }: { onCreate: (input: DiaryEntryInput) => Promise<void> }) {
  const [draft, setDraft] = useState({ date: today(), lesson_count: 1, content_taught: '' });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onCreate(draft);
      setDraft({ ...draft, content_taught: '' });
      toast.success('Aula registrada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar aula.'));
    }
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-2 gap-3 md:grid-cols-[1fr_0.7fr_3fr_auto]">
      <input type="date" required aria-label="Data da aula" value={draft.date} onChange={(e) => setDraft({ ...draft, date: e.target.value })} className={inputCls} />
      <select aria-label="Aulas no dia" value={draft.lesson_count} onChange={(e) => setDraft({ ...draft, lesson_count: Number(e.target.value) })} className={inputCls}>
        {[1, 2, 3, 4, 5, 6].map((n) => <option key={n} value={n}>{n} aula{n > 1 ? 's' : ''}</option>)}
      </select>
      <input required aria-label="Conteúdo ministrado" value={draft.content_taught} onChange={(e) => setDraft({ ...draft, content_taught: e.target.value })} placeholder="Conteúdo ministrado" className={`${inputCls} col-span-2 md:col-span-1`} />
      <button className={`${primaryButtonCls} col-span-2 md:col-span-1`}>Registrar</button>
    </form>
  );
}
