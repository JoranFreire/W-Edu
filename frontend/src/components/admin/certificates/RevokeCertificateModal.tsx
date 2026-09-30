'use client';

import { useState } from 'react';
import Modal from '@/components/common/Modal';

export default function RevokeCertificateModal({ onConfirm, onClose }: {
  onConfirm: (reason: string | null) => void;
  onClose: () => void;
}) {
  const [reason, setReason] = useState('');

  return (
    <Modal title="Revogar certificado" description="Informe o motivo da revogação, se houver." size="sm" onClose={onClose}>
      <textarea
        aria-label="Motivo da revogação"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        rows={4}
        placeholder="Motivo opcional"
        className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
      />
      <div className="mt-5 flex justify-end gap-3">
        <button type="button" onClick={onClose} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
          Cancelar
        </button>
        <button type="button" onClick={() => onConfirm(reason.trim() || null)} className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700">
          Revogar
        </button>
      </div>
    </Modal>
  );
}
