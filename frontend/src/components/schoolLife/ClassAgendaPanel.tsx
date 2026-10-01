'use client';

import toast from 'react-hot-toast';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { todayIso } from '@/lib/dates';
import { useClassAgenda } from '@/lib/hooks/schoolLife/useClassAgenda';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { AgendaItem } from '@/types/schoolLife';
import AgendaItemForm from './AgendaItemForm';
import AgendaList from './AgendaList';

/** Agenda da turma-grupo (proximos itens), com publicacao e remocao. */
export default function ClassAgendaPanel({ groupId, offeringId }: { groupId: number; offeringId: number | null }) {
  const { items, error, publish, remove } = useClassAgenda(groupId, todayIso());
  useErrorToast(error, 'Erro ao carregar a agenda.');

  const handleRemove = async (item: AgendaItem) => {
    if (!window.confirm(`Remover "${item.title}" da agenda?`)) return;
    try {
      await remove(item.id);
      toast.success('Item removido.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível remover.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Agenda da turma</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Alunos e responsáveis recebem um comunicado a cada publicação.</p>
      </div>
      <AgendaItemForm offeringId={offeringId} onSubmit={publish} />
      <AgendaList items={items} onRemove={handleRemove} />
    </section>
  );
}
