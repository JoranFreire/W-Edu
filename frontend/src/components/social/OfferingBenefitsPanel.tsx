'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { useOfferingBenefits } from '@/lib/hooks/social/useOfferingBenefits';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Entrega de beneficios no encontro (lanche so para quem esteve presente) e historico de entregas da turma. */
export default function OfferingBenefitsPanel({ offeringId }: { offeringId: number }) {
  const { benefits, error, deliver } = useOfferingBenefits(offeringId);
  const [draft, setDraft] = useState({ meetingId: '', itemId: '', quantity: '1' });
  useErrorToast(error, 'Erro ao carregar os benefícios.');
  if (!benefits) return <Spinner />;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const result = await deliver(Number(draft.meetingId), Number(draft.itemId), Number(draft.quantity));
      toast.success(`${result.delivered} entrega(s) registrada(s); estoque restante: ${result.remaining_stock}.`);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar a entrega.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Benefícios</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Registre a chamada antes: itens marcados como “só presentes” vão apenas para quem compareceu.</p>
      </div>
      <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <select required aria-label="Encontro da entrega" value={draft.meetingId} onChange={(e) => setDraft({ ...draft, meetingId: e.target.value })} className={inputCls}>
          <option value="">Encontro…</option>
          {benefits.meetings.map((meeting) => <option key={meeting.id} value={meeting.id}>{meeting.title} · {new Date(meeting.starts_at).toLocaleDateString('pt-BR')}</option>)}
        </select>
        <select required aria-label="Item entregue" value={draft.itemId} onChange={(e) => setDraft({ ...draft, itemId: e.target.value })} className={inputCls}>
          <option value="">Item…</option>
          {benefits.items.map((item) => <option key={item.id} value={item.id}>{item.name} (estoque {item.stock})</option>)}
        </select>
        <input required type="number" min={1} aria-label="Quantidade por aluno" value={draft.quantity} onChange={(e) => setDraft({ ...draft, quantity: e.target.value })} className={inputCls} />
        <button className={primaryButtonCls}>Registrar entrega</button>
      </form>
      {benefits.deliveries.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma entrega.</p> : (
        <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
          {benefits.deliveries.map((delivery) => (
            <li key={delivery.id} className="py-1 text-gray-800 dark:text-gray-200">
              {formatIsoDate(delivery.delivered_on)} · {delivery.item_name} × {delivery.quantity} · {delivery.student.name}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
