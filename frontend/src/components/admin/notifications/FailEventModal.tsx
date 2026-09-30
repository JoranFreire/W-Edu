'use client';

import { useState } from 'react';
import Modal from '@/components/common/Modal';

export default function FailEventModal({ onConfirm, onClose }: {
  onConfirm: (reason: string) => void;
  onClose: () => void;
}) {
  const [reason, setReason] = useState('');

  return (
    <Modal title="Marcar como falho" description="Informe o motivo da falha." size="sm" onClose={onClose}>
      <textarea aria-label="Motivo da falha" value={reason} onChange={(e) => setReason(e.target.value)} rows={4} className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white" />
      <div className="mt-5 flex justify-end gap-3">
        <button type="button" onClick={onClose} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">Cancelar</button>
        <button type="button" disabled={!reason.trim()} onClick={() => onConfirm(reason.trim())} className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-60">Marcar falha</button>
      </div>
    </Modal>
  );
}
