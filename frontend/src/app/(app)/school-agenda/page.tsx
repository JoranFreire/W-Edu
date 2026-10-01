'use client';

import AgendaList from '@/components/schoolLife/AgendaList';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { todayIso } from '@/lib/dates';
import { useMyAgenda } from '@/lib/hooks/schoolLife/useMyAgenda';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function SchoolAgendaPage() {
  const { items, loading, error } = useMyAgenda(todayIso());
  useErrorToast(error, 'Erro ao carregar a agenda.');

  if (loading && items.length === 0) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agenda escolar</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Tarefas, provas, eventos e avisos das suas turmas.</p>
      </div>
      <section className={sectionCls}><AgendaList items={items} showGroup /></section>
    </div>
  );
}
