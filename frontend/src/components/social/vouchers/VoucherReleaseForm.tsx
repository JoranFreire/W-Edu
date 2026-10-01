'use client';

import { useState } from 'react';
import { inputCls, primaryButtonCls } from '@/components/common/formStyles';
import { benefitKindLabels } from '@/lib/academic/socialLabels';
import { availableStock } from '@/lib/social/voucherStatus';
import type { VoucherDraft, VoucherTarget } from '@/lib/hooks/social/useOfferingVouchers';
import type { ScheduledMeeting } from '@/types/schedule';
import type { BenefitItem } from '@/types/socialPrograms';

interface Props {
  meetings: ScheduledMeeting[];
  items: BenefitItem[];
  students: { id: string; name: string }[];
  onSubmit: (draft: VoucherDraft) => Promise<void>;
}

type TargetKind = VoucherTarget['kind'];

/**
 * Libera o item para retirada com QR: lanche por encontro (so presentes), material, uniforme ou transporte
 * para a turma toda, ou qualquer item para um aluno.
 */
export default function VoucherReleaseForm({ meetings, items, students, onSubmit }: Props) {
  const [draft, setDraft] = useState({ target: 'offering' as TargetKind, meetingId: '', studentId: '', itemId: '', quantity: '1', validUntil: '' });
  const item = items.find((candidate) => candidate.id === draft.itemId);
  // Item so para presentes nao vai para a turma toda: o backend recusa, a tela nem oferece.
  const targetKind: TargetKind = item?.requires_attendance && draft.target === 'offering' ? 'meeting' : draft.target;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const target: VoucherTarget = targetKind === 'meeting'
      ? { kind: 'meeting', meetingId: draft.meetingId }
      : targetKind === 'student' ? { kind: 'student', studentId: draft.studentId } : { kind: 'offering' };
    await onSubmit({ target, itemId: draft.itemId, quantity: Number(draft.quantity), validUntil: draft.validUntil || null });
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-3">
      <select required aria-label="Item liberado" value={draft.itemId} onChange={(e) => setDraft({ ...draft, itemId: e.target.value })} className={inputCls}>
        <option value="">Item…</option>
        {items.map((option) => (
          <option key={option.id} value={option.id}>{option.name} · {benefitKindLabels[option.kind]} (disponível {availableStock(option)})</option>
        ))}
      </select>
      <select aria-label="Para quem" value={targetKind} onChange={(e) => setDraft({ ...draft, target: e.target.value as TargetKind })} className={inputCls}>
        <option value="offering" disabled={item?.requires_attendance}>Turma toda</option>
        <option value="meeting">{item?.requires_attendance ? 'Presentes no encontro' : 'Por encontro'}</option>
        <option value="student">Um aluno</option>
      </select>
      {targetKind === 'meeting' && (
        <select required aria-label="Encontro" value={draft.meetingId} onChange={(e) => setDraft({ ...draft, meetingId: e.target.value })} className={inputCls}>
          <option value="">Encontro…</option>
          {meetings.map((meeting) => <option key={meeting.id} value={meeting.id}>{meeting.title} · {new Date(meeting.starts_at).toLocaleDateString('pt-BR')}</option>)}
        </select>
      )}
      {targetKind === 'student' && (
        <select required aria-label="Aluno" value={draft.studentId} onChange={(e) => setDraft({ ...draft, studentId: e.target.value })} className={inputCls}>
          <option value="">Aluno…</option>
          {students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}
        </select>
      )}
      {targetKind === 'offering' && <span aria-hidden className="hidden md:block" />}
      <input required type="number" min={1} aria-label="Quantidade por aluno" value={draft.quantity} onChange={(e) => setDraft({ ...draft, quantity: e.target.value })} className={inputCls} />
      <input type="date" aria-label="Válido até (opcional)" title="Válido até (opcional)" value={draft.validUntil} onChange={(e) => setDraft({ ...draft, validUntil: e.target.value })} className={inputCls} />
      <button className={primaryButtonCls}>Liberar com QR</button>
    </form>
  );
}
