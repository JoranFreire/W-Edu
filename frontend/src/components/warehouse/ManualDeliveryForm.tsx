'use client';

import { useState } from 'react';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import type { MaterialRequest } from '@/types/warehouse';

/** Retirada sem o QR (ex.: professor sem celular): o motivo e obrigatorio e fica no historico. */
export default function ManualDeliveryForm({ request, onDeliver }: { request: MaterialRequest; onDeliver: (note: string) => Promise<void> }) {
  const [note, setNote] = useState('');
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onDeliver(note.trim());
  };
  return (
    <form onSubmit={submit} className="flex flex-wrap items-center gap-2">
      <input required minLength={3} aria-label={`Motivo da retirada sem QR de ${request.purpose}`} placeholder="Retirada sem QR: motivo"
        value={note} onChange={(e) => setNote(e.target.value)} className={`${inputCls} w-72`} />
      <button aria-label={`Registrar retirada de ${request.purpose}`} className={secondaryButtonCls}>Registrar retirada</button>
    </form>
  );
}
