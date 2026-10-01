'use client';

import { useState } from 'react';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { availableStock } from '@/lib/social/voucherStatus';
import type { MeetingVoucherDraft } from '@/lib/hooks/social/useOfferingVouchers';
import type { ScheduledMeeting } from '@/types/schedule';
import type { BenefitItem } from '@/types/socialPrograms';

interface Props {
  meetings: ScheduledMeeting[];
  items: BenefitItem[];
  onSubmit: (draft: MeetingVoucherDraft) => Promise<void>;
}

/** Libera o item no encontro para retirada com QR (so presentes, se o item exigir frequencia). */
export default function MeetingVoucherForm({ meetings, items, onSubmit }: Props) {
  const [draft, setDraft] = useState({ meetingId: '', itemId: '', quantity: '1', validUntil: '' });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSubmit({ meetingId: draft.meetingId, itemId: draft.itemId, quantity: Number(draft.quantity), validUntil: draft.validUntil || null });
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-5">
      <select required aria-label="Encontro" value={draft.meetingId} onChange={(e) => setDraft({ ...draft, meetingId: e.target.value })} className={inputCls}>
        <option value="">Encontro…</option>
        {meetings.map((meeting) => <option key={meeting.id} value={meeting.id}>{meeting.title} · {new Date(meeting.starts_at).toLocaleDateString('pt-BR')}</option>)}
      </select>
      <select required aria-label="Item liberado" value={draft.itemId} onChange={(e) => setDraft({ ...draft, itemId: e.target.value })} className={inputCls}>
        <option value="">Item…</option>
        {items.map((item) => <option key={item.id} value={item.id}>{item.name} (disponível {availableStock(item)})</option>)}
      </select>
      <input required type="number" min={1} aria-label="Quantidade por aluno" value={draft.quantity} onChange={(e) => setDraft({ ...draft, quantity: e.target.value })} className={inputCls} />
      <input type="date" aria-label="Válido até (opcional)" title="Válido até (opcional)" value={draft.validUntil} onChange={(e) => setDraft({ ...draft, validUntil: e.target.value })} className={inputCls} />
      <button className={primaryButtonCls}>Liberar com QR</button>
    </form>
  );
}
